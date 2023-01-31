import os.path
import pickle
import warnings
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.exceptions import ConvergenceWarning, DataConversionWarning


class MentalCommandClassifier:

    def __init__(self, uuid: int = 0, training_parameters: dict = None, file_name: str = None) -> None:
        # if file_name isn't given create it
        if file_name is None:
            self._uuid = uuid
            if training_parameters is None:
                self._classifier = None
            else:
                self._classifier = MLPClassifier(max_iter=training_parameters['number_of_generations'],
                                                 hidden_layer_sizes=training_parameters['hidden_layer_sizes'])

        # file_name is given load it from disk
        else:
            self.load(file_name)

        # remove the training warnings
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=DataConversionWarning)

    def train_classifier(self, training_data: list, training_labels: list) -> None:
        self._classifier.fit(training_data, training_labels)

    def get_error(self, data: list, label: list) -> float:
        return self._classifier.score(data, label)

    def get_losses(self) -> list:
        return self._classifier.loss_curve_

    def get_uuid(self) -> int:
        return self._uuid

    def get_number_of_generations(self) -> int:
        return self._classifier.get_params()['max_iter']

    def get_hidden_layer_sizes(self) -> list:
        return list(self._classifier.get_params()['hidden_layer_sizes'])

    def load(self, file_name: str) -> None:
        # if possible extract the uuid from the name
        try:
            self._uuid = int(file_name.split('.')[0])            # get uuid from the file name (es. 1.sav)
        except ValueError:
            pass

        file_path = os.path.join(os.path.abspath('..'), 'data', file_name)
        self._classifier = joblib.load(file_path)

    def store(self) -> None:
        file_path = os.path.join(os.path.abspath('..'), 'data', f'{self._uuid}.sav')
        joblib.dump(self._classifier, file_path)

    def rebuild(self, training_parameters: dict, uuid: int = None) -> None:
        if uuid is None:
            self._uuid += 1                              # autoincrement useful during the grid search
        else:
            self._uuid = uuid
        self._classifier = MLPClassifier(training_parameters)

    def serialize(self) -> dict:
        # convert to string and insert in a dictionary
        serialized_classifier = pickle.dumps(self._classifier).decode('ISO-8859-1')
        return {'classifier': serialized_classifier}
