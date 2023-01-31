import json
import os
from jsonschema import validate, ValidationError


class SessionCleaning:

    def correct_missing_samples(self, headset: list):
        """
        Checks for missing samples in the list of headset channels;
        if they are recoverable, the missing samples are corrected.
        :param headset: List of EEG channels.
        :return: True if there are no missing samples or the missing ones are recoverable.
        """
        for channel in range(len(headset)):
            # If a sample (a channel) is missing the interpolation is computed
            if not headset[channel]:
                print(f'[-] Channel nr. {channel + 1} is missing')
                if 7 <= channel <= 11:
                    self._interpolate_list(headset, channel)
                else:
                    return False
        return True

    @staticmethod
    def _interpolate_list(headset, channel):
        """
        Interpolates the specified channel with the adjacent ones in the headset.
        :param headset: List of EEG channels.
        :param channel: The channel to interpolate.
        :return: None
        """
        # List of adjacent channels in the EEG headset
        lists_to_use = [channel - 1, channel + 1, channel - 6, channel + 6]
        channel_length = len(headset[0])
        for i in range(channel_length):
            value = 0
            list_number = 0
            for j in lists_to_use:
                if headset[j]:
                    value += headset[j][i]
                    list_number += 1
            if list_number != 0:
                headset[channel].append(value / list_number)

    @staticmethod
    def correct_outliers(headset: list, min_eeg: int, max_eeg: int):
        """
        Corrects outliers in the EEG data of the different channels.
        :param headset: List of EEG channels.
        :param min_eeg: Minimum EEG value.
        :param max_eeg: Maximum EEG value.
        :return: None
        """
        for channel in headset:
            for i in range(len(channel)):
                if channel[i] > max_eeg:
                    channel[i] = max_eeg
                elif channel[i] < min_eeg:
                    channel[i] = min_eeg

    @staticmethod
    def validate_raw_session(raw_session: dict):
        """
        Validates the received raw session according to the loaded schema.
        :param raw_session: The dict containing the received raw session.
        :return: True if the raw session is valid, False if it is not valid.
        """
        try:
            with open(os.path.join(os.path.abspath('..'), 'data', 'raw_session_schema.json')) as f:
                schema = json.load(f)

            validate(raw_session, schema)
            return True

        except FileNotFoundError:
            print('[-] Failed to open schema file')
            return False

        except ValidationError:
            return False


