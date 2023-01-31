
LABELS_MAP = ["move", "stop", "left", "right"]


class MonitoringPhase:

    def __init__(self):
        """
        Constructor of the MonitoringPhase class.
        """
        self._execution_session_counter = 0
        self._monitoring_session_counter = 0
        self._label = None

    def increment_session_counter(self):
        """
        Increment the counter that represents the number of sessions received in the only Execution Phase
        :return: None
        """
        self._execution_session_counter += 1

    def check_threshold(self, execution_window_value: int, monitoring_window_value: int) -> bool:
        """
        Check if there is the 'Monitoring Phase'
        :param execution_window_value: value of the window in which the labels aren't sent to the MonitoringSystem
        :param monitoring_window_value: value of the window in which the labels are sent to the MonitoringSystem
        :return: True if the conditions to send the label are verified, False otherwise
        """
        if self._monitoring_session_counter < monitoring_window_value \
                and self._execution_session_counter > execution_window_value:
            self._monitoring_session_counter += 1
            print(f"***MonitoringPhase***   Execution session counter:{self._execution_session_counter}")
            print(f"***MonitoringPhase***   Monitoring session counter:{self._monitoring_session_counter}")
            return True
        elif self._monitoring_session_counter >= monitoring_window_value\
                and self._execution_session_counter > execution_window_value:
            self._execution_session_counter = 1
            self._monitoring_session_counter = 0
            print(f"***MonitoringPhase***   Execution session counter:{self._execution_session_counter}")
            print(f"***MonitoringPhase***   Monitoring session counter:{self._monitoring_session_counter}")
            return False
        else:
            print(f"***MonitoringPhase***   Execution session counter:{self._execution_session_counter}")
            print(f"***MonitoringPhase***   Monitoring session counter:{self._monitoring_session_counter}")
            return False

    def prepare_label(self, uuid: str, label_from_classifier: int) -> dict:
        """
        Receive the 'uuid' string of the current prepared session and the response of the classifier and produce the
        json to send to the MonitoringSystem
        :param uuid: uuid of the current prepared session
        :param label_from_classifier: value of the response of the classifier using the current prepared session
        :return: dict object that corresponds to the label to send
        """
        return {'uuid': uuid, 'label': LABELS_MAP[label_from_classifier]}
