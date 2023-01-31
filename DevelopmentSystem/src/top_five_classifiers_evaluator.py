import os
from src.mental_command_classifier import MentalCommandClassifier
from utility.logging import error


class TopFiveClassifierEvaluators:

    def __init__(self, dataset: dict) -> None:
        self._top_five_classifiers = []
        self._dataset = dataset

    def evaluate_new_classifier(self, new_classifier: MentalCommandClassifier) -> None:
        # compute validation error
        validation_error = new_classifier.get_error(self._dataset['validation_data'],
                                                    self._dataset['validation_labels'])

        # add new classifier with validation error in the list, orded by descending validation_error
        self._top_five_classifiers.append({'uuid': new_classifier.get_uuid(), 'validation_error': validation_error})
        self._top_five_classifiers = sorted(self._top_five_classifiers, key=lambda x: x["validation_error"],
                                            reverse=True)

        if len(self._top_five_classifiers) > 5:

            # if the new classifier is one of the top five remove from list and disk the sixth
            if self._top_five_classifiers[5]['uuid'] != new_classifier.get_uuid():
                # save classifier to disk
                new_classifier.store()

                # remove the sexth from disk
                try:
                    uuid_to_remove = self._top_five_classifiers[5]['uuid']
                    os.remove(os.path.join(os.path.abspath('..'), 'data', f'{uuid_to_remove}.sav'))
                except FileNotFoundError:
                    error('Serialized Classifier not found')
                    exit(1)

                # remove the sixth from the list
                self._top_five_classifiers = self._top_five_classifiers[:5]

            # if the new classifier isn't one of the top five remove it from list
            else:
                self._top_five_classifiers = self._top_five_classifiers[:5]

        else:
            # save classifier to disk
            new_classifier.store()

    def get_top_classifiers(self, number_of_generations: int, validation_error_threshold: float) -> dict:
        # structure of the report
        top_five_classifiers = {
            'number_of_generations': number_of_generations,
            'validation_error_threshold': validation_error_threshold,
            'classifiers': []
        }

        # iterate the top five classifier
        for classifier in self._top_five_classifiers:
            # reload the classifier from disk
            classifier_name = f'{classifier["uuid"]}.sav'
            mental_command_classifier = MentalCommandClassifier(file_name=classifier_name)

            # insert the classifier in the report
            info_classifier = {
                'uuid': classifier["uuid"],
                'hidden_layer_sizes': mental_command_classifier.get_hidden_layer_sizes(),
                'training_error': mental_command_classifier.get_error(self._dataset['training_data'],
                                                                      self._dataset['training_labels']),
                'validation_error': classifier['validation_error'],
                'actual_best': False
            }
            top_five_classifiers['classifiers'].append(info_classifier)

        return top_five_classifiers
