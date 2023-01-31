import os
import json
import pickle


class MentalCommandClassifier:

    def __init__(self):
        """
        Constructor of the MentalCommandClassifier class.
        """
        self._prepared_session = None
        self._best_classifier = None

    def deploy_classifier(self, json_file: dict) -> bool:
        """
        Receive a dict object that correspons to the best classifier selected by the DevelopmentSystem and save it on a
        .json file
        :param json_file: dict object that corresponds to the best classifier
        :return: boolean value that represents if the save operation is ended correctly or not.
        """
        if json_file is None:
            print('No classifier received')
            return False

        received_json_path = os.path.join(os.path.abspath('..'), 'data', 'mental_command_classifier.json')
        try:
            with open(received_json_path, 'w') as f:
                json.dump(json_file, f)
        except IOError:
            print("Failed to load classifier on the .json file")
            exit(1)
        print("***Execution System***   Deployment completed successfully")
        return True

    def execute_classifier(self) -> int:
        """
        Load the best classifier through the 'loads' of the pickle library.
        Execute the best classifier using the prepare session previously received and produce a final value
        :return: int value that will correspond to a command for the wheelchair.
        """
        try:
            mlp_classifier = pickle.loads(self._best_classifier['classifier'].encode('ISO-8859-1'))
            # the final label from the classifier is generated
            session = [self._prepared_session['features']]
            return mlp_classifier.predict(session)
        except UnicodeDecodeError:
            print("***Execution System*** Label's production failed, classifier not decodable!")
            print("***Execution System terminated***")
            exit(1)
