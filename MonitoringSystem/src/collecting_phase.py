from utility.logging import info


class CollectingPhase:

    def __init__(self, labels_threshold):
        self.counter_session_labels = 0
        self.labels_threshold = labels_threshold

    def increment_counter(self):
        self.counter_session_labels += 1

    def reset_counter(self):
        info("CollectingPhase - Labels counter set to 0, to produce a new Accuracy Report\n")
        self.counter_session_labels = 0

    def check_labels_threshold(self):
        if self.counter_session_labels < self.labels_threshold:
            return False
        else:
            return True

    def get_counter_session_labels(self):
        return self.counter_session_labels
