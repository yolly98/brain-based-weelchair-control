from utility.logging import warning


class RawSessionIntegrity:

    def mark_missing_samples(self, headset_eeg: list, threshold: int) -> bool:
        """
        Detects and marks the missing headset EEG data in a Raw Session.
        :param headset_eeg: list of EEG data (represented as list of integers)
        :param threshold: maximum threshold of missing samples tolerated
        :return: True if the number of missing samples detected meets the requirements. False otherwise.
        """

        missing_samples = 0
        for i in range(0, len(headset_eeg)):
            if not headset_eeg[i]:
                # warning(f'[CHANNEL {i+1}] EEG Data not found')
                missing_samples += 1

        # warning(f'Missing samples detected: {missing_samples}')
        return missing_samples <= threshold
