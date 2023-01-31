from src.mental_command_classifier import MentalCommandClassifier
from src.test_report_generator import TestReportGenerator


class TestController:

    def __init__(self, mental_command_classifier: MentalCommandClassifier = None) -> None:
        self._mental_command_classifier = mental_command_classifier

    def run(self, operational_mode: str, testing: bool = False, dataset: dict = None,
            test_error_threshold: float = None) -> bool:
        if operational_mode == 'test_best_classifier':
            # get training and test errors
            errors = {
                'training_error': self._mental_command_classifier.get_error(dataset['training_data'],
                                                                            dataset['training_labels']),
                'test_error': self._mental_command_classifier.get_error(dataset['test_data'], dataset['test_labels'])
            }

            # prepare parameters needed for the report
            training_parameters = {
                'number_of_generations':  self._mental_command_classifier.get_number_of_generations(),
                'hidden_layer_sizes': self._mental_command_classifier.get_hidden_layer_sizes()
            }

            # generate the report
            TestReportGenerator().generate_report(training_parameter=training_parameters,
                                                  errors=errors,
                                                  test_error_threshold=test_error_threshold,
                                                  testing=testing)

        elif operational_mode == 'check_test_report':
            return TestReportGenerator().evaluate_report()
