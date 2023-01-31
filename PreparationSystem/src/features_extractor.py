import numpy as np
from scipy.signal import welch
from scipy.integrate import simps


class FeaturesExtractor:
    """
    Class that extracts features and prepares the session to be sent.
    """

    def extract_features(self, features: dict, raw_session: dict, prepared_session: dict, operative_mode: str):
        """
        Extracts the relevant features from the raw EEG session data.
        :param features: Dictionary of features to extract from raw EEG session data.
        :param raw_session: Raw EEG session data.
        :param prepared_session: Dictionary to store the prepared session to send.
        :param operative_mode: Execution or development mode.
        :return: None
        """
        delta, theta, alpha, beta = self._extract_headset_features(raw_session['headset'], features)
        if operative_mode == 'development':
            self._prepare_session_development(raw_session, prepared_session, delta, theta, alpha, beta)
        elif operative_mode == 'execution':
            self._prepare_session_execution(raw_session, prepared_session, delta, theta, alpha, beta, features)

    def _extract_headset_features(self, headset: list, features: dict):
        """
        Extracts the relevant features from the headset data of the raw EEG session data.
        :param headset: List of channels in the EEG headset.
        :param features: Dictionary of features to extract from the headset data.
        :return: Lists of extracted features in the different frequency bands.
        """
        delta, theta, alpha, beta = [], [], [], []
        for channel in headset:
            delta.append(self._compute_average_power(channel, features['delta_wave']['start_frequency'],
                                                     features['delta_wave']['end_frequency']))
            theta.append(self._compute_average_power(channel, features['theta_wave']['start_frequency'],
                                                     features['theta_wave']['end_frequency']))
            alpha.append(self._compute_average_power(channel, features['alpha_wave']['start_frequency'],
                                                     features['alpha_wave']['end_frequency']))
            beta.append(self._compute_average_power(channel, features['beta_wave']['start_frequency'],
                                                    features['beta_wave']['end_frequency']))
        return delta, theta, alpha, beta

    @staticmethod
    def _compute_average_power(headset: list, start_frequency: int, end_frequency: int) -> float:
        """
        Computes the average power in a specified frequency range.
        :param headset: List of voltage data to compute average power on.
        :param start_frequency: Starting frequency of the range in which to compute the average power in.
        :param end_frequency: End frequency of the range in which to compute the average power in.
        :return: Average power in the specified frequency range.
        """
        sampling_frequency = 250
        window_seconds = 1.25
        # Define segment length
        segment_length = window_seconds * sampling_frequency

        # Compute the modified periodogram (Welch)
        frequencies, psd = welch(headset, sampling_frequency, nperseg=segment_length)

        # Frequency resolution
        frequency_resolution = frequencies[1] - frequencies[0]

        # Find intersecting values in frequency vector
        intersecting_bands = np.logical_and(frequencies >= start_frequency, frequencies <= end_frequency)

        # Integral approximation of the spectrum using Simpson's rule.
        return simps(psd[intersecting_bands], dx=frequency_resolution)

    @staticmethod
    def _prepare_session_development(raw_session: dict, prepared_session: dict, delta: list, theta: list,
                                     alpha: list, beta: list):
        """
        Prepares the session (development mode).
        :param raw_session: Raw session data.
        :param prepared_session: Dictionary to store the prepared session to be sent.
        :param delta: Average power on the delta frequency band.
        :param theta: Average power on the theta frequency band.
        :param alpha: Average power on the alpha frequency band.
        :param beta: Average power on the beta frequency band.
        :return: None
        """
        prepared_session['uuid'] = raw_session['uuid']
        prepared_session['features'] = {}
        prepared_session['features']['delta'] = delta
        prepared_session['features']['theta'] = theta
        prepared_session['features']['alpha'] = alpha
        prepared_session['features']['beta'] = beta
        prepared_session['features']['environment'] = raw_session['environment']
        prepared_session['calendar'] = raw_session['calendar']
        prepared_session['command_thought'] = raw_session['command_thought']

    @staticmethod
    def _prepare_session_execution(raw_session: dict, prepared_session: dict, delta: list, theta: list,
                                   alpha: list, beta: list, features: dict):
        """
        Prepares the session (execution mode).
        :param raw_session: Raw session data.
        :param prepared_session: Dictionary to store the prepared session to be sent.
        :param delta: Average power on the delta frequency band.
        :param theta: Average power on the theta frequency band.
        :param alpha: Average power on the alpha frequency band.
        :param beta: Average power on the beta frequency band.
        :param features: Dictionary that stores the features.
        :return: None
        """
        prepared_session['uuid'] = raw_session['uuid']
        # Take the numeric value corresponding to the value of environment in raw session
        environment = features['environment'][raw_session['environment']]
        prepared_session['features'] = alpha + beta + delta + theta + [environment]
