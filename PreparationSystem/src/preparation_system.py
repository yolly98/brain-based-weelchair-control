import json
import os
from datetime import datetime
from threading import Thread
from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from src.session_cleaning import SessionCleaning
from src.features_extractor import FeaturesExtractor


class PreparationSystem:
    """
    Class that controls the execution of the Preparation System calling all the necessary functions to produce
    the prepared session from the raw one.
    """

    def __init__(self):
        """
        Initializes the PreparationSystem class, validates the configuration and sets the instance variables
        for raw and prepared sessions.
        """
        self._preparation_system_configuration = self._validate_configuration()
        print(f'[+] The configuration is valid, {self._preparation_system_configuration["operative_mode"]} mode')
        self._raw_session = None
        self._prepared_session = None

    def run(self):
        """
        Method that runs all the instructions needed for session preparation.
        It continuously listens for new raw sessions, processes them, extracts features,
        prepares the session and sends it to the corresponding endpoint based on the current operating mode.
        :return: None
        """
        # Start the Flask app listener on the port specified
        listener_thread = Thread(target=JsonIO.get_instance().listener, args=('0.0.0.0', 5000), daemon=True)
        listener_thread.start()

        while True:
            # Get received raw session
            self._raw_session = JsonIO.get_instance().get_received_json()
            print('[+] Raw session received')

            # Check raw session validity
            if SessionCleaning.validate_raw_session(self._raw_session):
                print('[+] Raw session is valid')
            else:
                print('[-] Raw session is not valid')
                continue

            # Correct missing samples
            if SessionCleaning().correct_missing_samples(self._raw_session['headset']):
                print('[+] Headset samples ok')
            else:
                print('[-] Missing samples are unrecoverable, raw session discarded')
                continue

            # Correct outliers
            SessionCleaning.correct_outliers(self._raw_session['headset'],
                                             self._preparation_system_configuration['min_eeg'],
                                             self._preparation_system_configuration['max_eeg'])

            # Extract features and prepare session
            self._prepared_session = {}
            FeaturesExtractor().extract_features \
                (self._preparation_system_configuration['features'], self._raw_session, self._prepared_session,
                 self._preparation_system_configuration['operative_mode'])
            print('[+] Features extracted and session prepared')

            # Send prepared session to the endpoint corresponding to the current operating mode
            if self._preparation_system_configuration['operative_mode'] == 'development':
                if JsonIO.get_instance().send(self._preparation_system_configuration['segregation_endpoint_IP'],
                                              self._preparation_system_configuration['segregation_endpoint_port'],
                                              self._prepared_session):
                    print(f'[+] Prepared session sent at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

            elif self._preparation_system_configuration['operative_mode'] == 'execution':
                if JsonIO.get_instance().send(self._preparation_system_configuration['execution_endpoint_IP'],
                                              self._preparation_system_configuration['execution_endpoint_port'],
                                              self._prepared_session):
                    print(f'[+] Prepared session sent at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        exit(0)

    @staticmethod
    def _validate_configuration():
        """
        Validates the configuration according to the loaded schema
        :return: The configuration if it is valid.
        """
        try:
            # Load configuration from file
            with open(os.path.join(os.path.abspath('..'), 'preparation_system_configuration.json')) as f:
                configuration = json.load(f)
            # Load schema from file
            with open(os.path.join(os.path.abspath('..'), 'data', 'configuration_schema.json')) as f:
                configuration_schema = json.load(f)

            # Validate configuration schema
            validate(configuration, configuration_schema)
            return configuration

        except FileNotFoundError:
            print('Failed to open configuration file')
            exit(1)

        except ValidationError:
            print('Config validation failed')
            exit(1)


if __name__ == '__main__':
    try:
        PreparationSystem().run()
    except KeyboardInterrupt:
        print('Preparation System terminated')
        exit(0)
