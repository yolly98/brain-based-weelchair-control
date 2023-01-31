import json
import os
from typing import Any

from jsonschema import validate, ValidationError

from src.mental_command_classifier import MentalCommandClassifier
from src.top_five_classifiers_evaluator import TopFiveClassifierEvaluators
from src.top_five_classifiers_report_generator import TopFiveClassifiersReportGenerator
from utility.logging import info, trace, error


class ValidationController:

    def __init__(self, mental_command_classifier: MentalCommandClassifier = None,
                 number_of_hidden_layers_range: list = None, number_of_hidden_neurons_range: list = None) -> None:
        self._mental_command_classifier = mental_command_classifier
        self._number_of_hidden_layers_range = number_of_hidden_layers_range
        self._number_of_hidden_neurons_range = number_of_hidden_neurons_range

    def run(self, operational_mode: str, testing: bool = False, dataset: dict = None,
            validation_error_threshold: float = None) -> int:
        if operational_mode == 'grid_search':
            top_five_classifiers_evaluator = TopFiveClassifierEvaluators(dataset)
            self._mental_command_classifier = MentalCommandClassifier()

            # prepare the combinations of parameters
            number_of_generations, training_parameters_combinations = self._generate_training_parameters_combinations()
            number_of_combinations = len(training_parameters_combinations)
            info(f'Grid Search with {number_of_combinations} combinations of parameters')
            counter = 0

            # grid search
            for parameters in training_parameters_combinations:
                # create and train a classifier with the new parameters
                self._mental_command_classifier.rebuild(parameters)
                self._mental_command_classifier.train_classifier(dataset['training_data'], dataset['training_labels'])

                # evaluate if is one of the top five
                top_five_classifiers_evaluator.evaluate_new_classifier(new_classifier=self._mental_command_classifier)

                counter += 1
                trace(f'{round((counter / number_of_combinations) * 100)}% of Grid Search completed')

            # generate the report
            TopFiveClassifiersReportGenerator().generate_report(
                top_five_classifiers=top_five_classifiers_evaluator.get_top_classifiers(
                    number_of_generations=number_of_generations,
                    validation_error_threshold=validation_error_threshold),
                testing=testing)

        elif operational_mode == 'check_top_five_classifiers_report':
            return TopFiveClassifiersReportGenerator().evaluate_report()

    def _generate_training_parameters_combinations(self) -> tuple[Any, list[tuple[int, ...]]]:
        # load number of generations file and schema
        with open(os.path.join(os.path.abspath('..'), 'data', 'number_of_generations.json')) as f:
            number_of_generations_file = json.load(f)
        with open(os.path.join(os.path.abspath('..'), 'resources', 'number_of_generations_schema.json')) as f:
            number_of_generations_schema = json.load(f)

        # validate number of generations
        try:
            validate(number_of_generations_file, number_of_generations_schema)
            number_of_generations = number_of_generations_file['number_of_generations']
        except ValidationError:
            error('Number of generations validation failed')
            exit(1)

        # compute the possible number of neurons with descending logarithm
        number_of_neurons = [self._number_of_hidden_neurons_range[-1]]
        while True:
            new_value = int(number_of_neurons[-1] / 2)
            if new_value >= 1:
                number_of_neurons.append(new_value)
            else:
                break

        # compute the possible configuration based on the possible number of layers
        combinations = []
        parameters = {'max_iter': number_of_generations}
        for number_of_layers in range(self._number_of_hidden_layers_range[0],
                                      self._number_of_hidden_layers_range[1] + 1):
            if number_of_layers > len(number_of_neurons):
                hidden_layer_sizes = tuple(number_of_neurons + [1] * (number_of_layers - len(number_of_neurons)))
                combinations.append(hidden_layer_sizes)
                parameters['hidden_layer_sizes'] = hidden_layer_sizes
            elif number_of_layers == len(number_of_neurons):
                hidden_layer_sizes = tuple(number_of_neurons)
                combinations.append(hidden_layer_sizes)
                parameters['hidden_layer_sizes'] = hidden_layer_sizes
            else:
                for i in range(len(number_of_neurons) - number_of_layers):
                    hidden_layer_sizes = tuple(number_of_neurons[i: number_of_layers + i])
                    combinations.append(hidden_layer_sizes)
                    parameters['hidden_layer_sizes'] = hidden_layer_sizes

        return number_of_generations, combinations
