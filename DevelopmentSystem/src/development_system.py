import json
import os.path
from threading import Thread
from jsonschema import validate, ValidationError

from src.early_training_controller import EarlyTrainingController
from src.json_io import JsonIO
from src.learning_session_store import LearningSessionStore
from src.mental_command_classifier import MentalCommandClassifier
from src.test_controller import TestController
from src.validation_controller import ValidationController
from utility.logging import info, error, success, warning

ACCEPTED_OPERATIONAL_MODES = ['waiting_for_dataset', 'early_training', 'check_early_training_report', 'grid_search',
                              'check_top_five_classifiers_report', 'test_best_classifier', 'check_test_report']


class DevelopmentSystem:

    def __init__(self) -> None:
        # open config and schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'development_system_config_schema.json')) as f:
            config_schema = json.load(f)
        with open(os.path.join(os.path.abspath('..'), 'development_system_config.json')) as f:
            self.config = json.load(f)

        # validate the config
        try:
            validate(self.config, config_schema)
        except ValidationError:
            error('Config validation failed')
            exit(1)

        self.mental_command_classifier = None
        self._learning_session_store = LearningSessionStore()

    def run(self) -> None:
        # check if operational mode is valid
        if self.config["operational_mode"] not in ACCEPTED_OPERATIONAL_MODES:
            error(f'Invalid operational mode: \'{self.config["operational_mode"]}\'')
            exit(1)

        info(f'Development System started on main thread in \'{self.config["operational_mode"]}\' mode')

        # start the rest server in a new thread as daemon
        run_thread = Thread(target=JsonIO.get_instance().listen, args=('0.0.0.0', 5000))
        run_thread.setDaemon(True)
        run_thread.start()

        # main cycle
        while True:
            # ====================== Receive dataset ======================

            if self.config['operational_mode'] == 'waiting_for_dataset':
                # get new received learning set and save in the learning session store
                learning_session_set = JsonIO.get_instance().get_queue().get(block=True)
                res = self._learning_session_store.store_dataset(received_dataset=learning_session_set)

                # if the store fails restart from 'waiting_for_dataset'
                if res is False:
                    continue

                # create JSON file containing the number of generations
                with open(os.path.join(os.path.abspath('..'), 'data', 'number_of_generations.json'), "w") as f:
                    json.dump({'number_of_generations': self.config['initial_number_of_generations']}, f, indent=4)

                # change operational mode to early training
                self._change_operational_mode('early_training')

            # ====================== Early training =======================

            if self.config['operational_mode'] == 'early_training':
                # get dataset from learning session store
                training_dataset = self._learning_session_store.get_training_set()

                # start the early training controller
                EarlyTrainingController(mental_command_classifier=self.mental_command_classifier,
                                        number_of_hidden_layers_range=self.config['number_of_hidden_layers_range'],
                                        number_of_hidden_neurons_range=self.config['number_of_hidden_neurons_range']) \
                    .run(operational_mode=self.config['operational_mode'],
                         testing=self.config['testing_mode'],
                         training_dataset=training_dataset)

                # change operational mode and stop (if testing mode instead continue)
                self._change_operational_mode('check_early_training_report')
                if self.config['testing_mode'] is False:
                    break
                else:
                    continue

            # ====================== Early training Report Evaluation ======================

            if self.config['operational_mode'] == 'check_early_training_report':
                # the early training controller will return the ML Engineer evaluation
                report_evaluation = EarlyTrainingController().run(operational_mode=self.config['operational_mode'])
                if report_evaluation is True:
                    success('The Number of Generations is good, Early Training ended')
                    self._change_operational_mode('grid_search')
                else:
                    warning('The Number of Generations has changed, restart from Early Training')
                    self._change_operational_mode('early_training')

            # ====================== Grid search =======================

            if self.config['operational_mode'] == 'grid_search':
                # get training and validation sets from database
                training_dataset = self._learning_session_store.get_training_set()
                validation_dataset = self._learning_session_store.get_validation_set()

                # start the validation controller
                ValidationController(mental_command_classifier=self.mental_command_classifier,
                                     number_of_hidden_layers_range=self.config['number_of_hidden_layers_range'],
                                     number_of_hidden_neurons_range=self.config['number_of_hidden_neurons_range']) \
                    .run(operational_mode=self.config['operational_mode'],
                         testing=self.config['testing_mode'],
                         dataset=training_dataset | validation_dataset,
                         validation_error_threshold=self.config['validation_error_threshold'])

                # change operational mode and stop (if testing mode instead continue)
                self._change_operational_mode('check_top_five_classifiers_report')
                if self.config['testing_mode'] is False:
                    break
                else:
                    continue

            # ====================== Top Five Classifiers Report Evaluation ======================

            if self.config['operational_mode'] == 'check_top_five_classifiers_report':
                # the validation controller will return the uuid of the best classifier (-1 if there isn't)
                best_classifier_uuid = ValidationController().run(operational_mode=self.config['operational_mode'])
                if best_classifier_uuid == -1:
                    warning('No valid Best Classifier found, restart from Early Training with new Number of '
                            'Generations')
                    self._change_operational_mode('early_training')
                else:
                    success(f'Best Classifier found with UUID:{best_classifier_uuid}, Validation Phase ended')
                    self._change_operational_mode('test_best_classifier')

                    # rename classifier on disk (for easier recovery in the future)
                    old_name = os.path.join(os.path.abspath('..'), 'data', f'{best_classifier_uuid}.sav')
                    new_name = os.path.join(os.path.abspath('..'), 'data', 'best_classifier.sav')
                    try:
                        os.rename(old_name, new_name)
                    except FileExistsError:
                        os.remove(new_name)
                        os.rename(old_name, new_name)

                    # load from disk the best classifier
                    self.mental_command_classifier = MentalCommandClassifier(file_name='best_classifier.sav')

                # remove unused classifiers from disk
                self._remove_serialized_classifiers()

            # ====================== Test Best Classifier =======================

            if self.config['operational_mode'] == 'test_best_classifier':
                # load the classifier from disk if None (recovery from crash during test)
                if self.mental_command_classifier is None:
                    self.mental_command_classifier = MentalCommandClassifier(file_name='best_classifier.sav')

                # get training and test sets from database
                training_dataset = self._learning_session_store.get_training_set()
                test_dataset = self._learning_session_store.get_test_set()

                # start test controller
                TestController(mental_command_classifier=self.mental_command_classifier) \
                    .run(operational_mode=self.config['operational_mode'],
                         testing=self.config['testing_mode'],
                         dataset=training_dataset | test_dataset,
                         test_error_threshold=self.config['test_error_threshold'])

                # remove training, validation and test sets from learning session store
                self._learning_session_store.delete_dataset()

                # change operational mode and stop (if testing mode instead continue)
                self._change_operational_mode('check_test_report')
                if self.config['testing_mode'] is False:
                    break
                else:
                    continue

            # ====================== Test Report Evaluation ======================

            if self.config['operational_mode'] == 'check_test_report':
                # load the classifier from disk
                self.mental_command_classifier = MentalCommandClassifier(file_name='best_classifier.sav')

                # the test controller will return the ML Engineer evaluation
                report_evaluation = TestController(mental_command_classifier=self.mental_command_classifier) \
                    .run(operational_mode=self.config['operational_mode'])
                if report_evaluation is True:
                    info('The Best Classifier is valid, can be sent to Execution System')

                    # send serialized classifier to execution system
                    serialized_classifier = self.mental_command_classifier.serialize()
                    JsonIO.get_instance().send(ip_endpoint=self.config['ip_endpoint'],
                                               port_endpoint=self.config['port_endpoint'],
                                               classifier=serialized_classifier)

                    # restart workflow
                    self._change_operational_mode('waiting_for_dataset')
                else:
                    warning('The Best Classifier isn\'t valid, Reconfiguration of the Systems are needed')
                    self._change_operational_mode('waiting_for_dataset')

                    # if not in testing mode stop, otherwise restart from waiting dataset
                    if self.config['testing_mode'] is False:
                        break
                    else:
                        continue

        # close all threads
        exit(0)

    def _change_operational_mode(self, new_mode: str) -> None:
        self.config['operational_mode'] = new_mode

        # save the new version of config
        with open(os.path.join(os.path.abspath('..'), 'development_system_config.json'), "w") as f:
            json.dump(self.config, f, indent=4)

        info(f'Switch to \'{new_mode}\' operational mode')

    def _remove_serialized_classifiers(self) -> None:
        path = os.path.join(os.path.abspath('..'), 'data')

        for file in os.listdir(path):
            if file.endswith('.sav') and file != 'best_classifier.sav':
                os.remove(os.path.join(path, file))
