import json
import os
import csv
import time

from threading import Thread
from src.json_io import JsonIO
from src.mental_command_classifier import MentalCommandClassifier
from src.monitoring_phase import MonitoringPhase
from jsonschema import validate, ValidationError


TESTING_THRESHOLD = 1000


class ExecutionSystem:

    def __init__(self):
        """
        Constructor of the ExecutionSystem class
        """
        self._configuration_execution_system = self._validate_configuration()

    def _open_json_file(self, path: str) -> dict:
        """
        :param path: path of the .json file to open
        :return: dict object that represent the .json file
        """
        try:
            with open(path) as file:
                json_file = json.load(file)

        except FileNotFoundError:
            print('***Execution System***   Failed to open file')
            exit(1)

        return json_file

    def _validate_configuration(self) -> dict:
        """
        Use the function 'open_json_file' to load the configuration file of the System and the validator for it.
        Use the 'validate' function to check if the .json file is structured as the validator says.
        :return: the configuration as a dict object, if the check is passed
        """
        try:
            # load configuration file
            configuration = \
                self._open_json_file(os.path.join(os.path.abspath('..'), 'configuration_execution_system.json'))

            # load validator file
            validator_schema = \
                self._open_json_file\
                    (os.path.join(os.path.abspath('..'), 'configuration_execution_system_validator.json'))

            # validate json
            validate(configuration, validator_schema)
            print("***Execution System***   Validation complete")
            return configuration

        except ValidationError:
            print('***Execution System***   Config validation failed')
            exit(1)

    def validate_input(self, json_object: dict, json_schema: str) -> bool:
        """
        Use the function 'open_json_file' to load the validator for the json input object.
        Use the 'validate' function to check if the .json file is structured as the validator says.
        :param json_object: dict object of the .json file to validate
        :param json_schema: filepath of the validator for the json input object
        :return: True if the check is passed, False otherwise.
        """
        try:
            # load validator schema
            validator_schema = self._open_json_file(json_schema)
            validate(json_object, validator_schema)
            return True
        except ValidationError:
            print("***Execution System*** json validation failed")
            return False

    def _save_result_on_csv(self, filepath: str, arriving_timestamp: float = None, uuid: str = None):
        """
        *** For testing purpose ***
        Save the timestamp in which a classifier is correctly deployed into a row of a .csv file
        :param filepath: path of the .csv file in which the results must be saved
        :return: Noneexecution
        """
        time_stamp = time.time()
        with open(filepath, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            if self._configuration_execution_system['operating_mode'] == 'development':
                csvwriter.writerow([time_stamp])
            else:
                csvwriter.writerow([uuid, arriving_timestamp, time_stamp])

    def run(self):
        """
        Main function of the ExecutionSystem class that calls also the methods of other classes in order to:

        *** Development Phase ***
        - Deploy correctly a classifier that is received from the DeploymentSystem saving it in a file .json and
        stopping the module execution to switch in a "execution mode".

        *** Execution Phase ***
        - Receive correctly a prepared session from the PreparedSystem and produce the value that corresponds to
        the command that the user thought.
        - If the number of sessions received is equal or greater than a certain threshold, the module will send the next
        produced labels also to the MonitoringSystem
        :return: None
        """
        listener_thread = Thread(target=JsonIO.get_instance().listener, args=('0.0.0.0', 5000))
        listener_thread.setDaemon(True)
        listener_thread.start()
        print(f"MODE SELECTED: {self._configuration_execution_system['operating_mode']}")
        print(f"MODE TESTING: {self._configuration_execution_system['testing']}")
        mental_command_classifier_instance = MentalCommandClassifier()
        monitoring_instance = MonitoringPhase()
        counter_testing = 0
        while True:
            if self._configuration_execution_system['operating_mode'] == 'development':
                json_file = JsonIO.get_instance().get_received_json()
                # if there is the development flow, the best classifier is received and, after the validation check, is
                # saved on a file
                if not self.validate_input(json_file, os.path.join(os.path.abspath('..'), 'classifier_validator.json')):
                    print("***Execution System*** Classifier validation failed")
                    continue
                if mental_command_classifier_instance.deploy_classifier(json_file):
                    if self._configuration_execution_system['testing']:
                        self._save_result_on_csv\
                            (os.path.join(os.path.abspath('..'), f'development_{TESTING_THRESHOLD}_classifier.csv'))
                        counter_testing += 1
                        print(f"*** (TEST) Execution System***   N. of classifiers collected: {counter_testing}")
                        if counter_testing == TESTING_THRESHOLD:
                            print("*** (TEST) Execution System***   Classifiers collection finished")
                            exit(0)
                        else:
                            continue
                    exit(0)

            else:
                # if there is the execution flow:
                # the prepared session is received
                mental_command_classifier_instance._prepared_session = JsonIO.get_instance().get_received_json()
                if not self.validate_input(mental_command_classifier_instance._prepared_session,
                                           os.path.join(os.path.abspath('..'), 'prepared_session_validator.json')):
                    print("***Execution System*** Prepared session validation failed")
                    continue
                # the counter of the Monitoring Phase is incremented
                monitoring_instance.increment_session_counter()
                # the best classifier from the .json file is loaded
                mental_command_classifier_instance._best_classifier = self._open_json_file(os.path.join
                                            (os.path.abspath('..'), 'data', 'mental_command_classifier.json'))
                # print(classifier)
                # the response of the classifier is computed
                arriving_timestamp = time.time()
                final_label = list(mental_command_classifier_instance.execute_classifier())[0]
                if self._configuration_execution_system['testing']:
                    self._save_result_on_csv\
                        (os.path.join(os.path.abspath('..'), f'execution_{TESTING_THRESHOLD}_sessions.csv'),
                                             arriving_timestamp, mental_command_classifier_instance._prepared_session['uuid'])
                    counter_testing += 1
                    print(f"*** (TEST) Execution System***   N. of sessions collected: {counter_testing}")
                    if counter_testing == TESTING_THRESHOLD:
                        print("*** (TEST) Execution System***   Sessions collection finished")
                        exit(0)
                # the label is sent to the client
                print(f"***Execution System***   The final prediction is: {final_label}")
                if monitoring_instance.check_threshold(self._configuration_execution_system['execution_window_value'],
                                                       self._configuration_execution_system['monitoring_window_value']):
                # if the number of session received is equal or greater than the threshold:
                # the final label is prepared for the monitoring system
                    label_to_send = monitoring_instance.prepare_label \
                        (mental_command_classifier_instance._prepared_session['uuid'], final_label)
                    print(f"***Execution System***   The label to send is: {label_to_send}")
                # the label is sent to the monitoring system
                    JsonIO.get_instance().send(self._configuration_execution_system['endpoint_IP'],
                                                    self._configuration_execution_system['endpoint_port'], label_to_send)
        exit(0)


if __name__ == '__main__':
    try:
        ExecutionSystem().run()
    except KeyboardInterrupt:
        print("***Execution System terminated***")
        exit(0)
