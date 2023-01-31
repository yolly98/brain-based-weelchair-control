import json
import os
import random
from time import time, sleep

from pandas import read_csv, DataFrame
from requests import post, exceptions

from utility.logging import error, info_simulation, warning_simulation, trace

INGESTION_SYSTEM_IP = 'localhost'
INGESTION_SYSTEM_PORT = 4000
MISSING_SAMPLES = [9, 10, 11]

TESTING_MODE = True  # Enables timestamp saving
DATASET_TO_SEND = 100  # Dataset to test during the testing mode

CONFIG_FILENAME = 'ingestion_system_config.json'


def save_timestamp():
    t = time()
    df = DataFrame([[t]], columns=['Timestamp'])
    df.to_csv(f'timestamp-{t}.csv', index=False)


def is_queue_full() -> bool:
    try:
        with open(os.path.join(os.path.abspath('..'), 'data', 'queue_size.txt'), 'r') as f:
            queue_size = int(f.read())
            return queue_size > 2000
    except FileNotFoundError:
        return False
    except ValueError:
        return False


class DataSourcesSimulation:
    def __init__(self):
        with open(os.path.join(os.path.abspath('..'), 'resources', CONFIG_FILENAME)) as f:
            loaded_json = json.load(f)
            self.operative_mode = loaded_json['operative_mode']

            if self.operative_mode == 'execution':
                self.execution_window = loaded_json['execution_window']
                self.monitoring_window = loaded_json['monitoring_window']
                self.missing_samples_threshold = loaded_json['missing_samples_threshold']
                self.sessions_executed = 0
                self.sessions_monitored = 0
                self.monitoring = False

        self.dataset_length = None
        self.dataset = None

    def send_record(self, data: dict) -> None:
        try:
            post(url=connection_string, json=data)
        except exceptions.RequestException:
            error('Ingestion System unreachable')
            exit(-1)

    def read_dataset(self) -> None:
        calendar = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_calendar.csv'))
        set_calendar = calendar.rename(columns={'CALENDAR': 'calendar', 'TIMESTAMP': 'timestamp', 'UUID': 'uuid'})

        headset = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_headset.csv'))
        set_headset = headset.rename(columns={'CHANNEL': 'channel', 'TIMESTAMP': 'timestamp', 'UUID': 'uuid'})

        settings = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_setting.csv'))
        set_settings = settings.rename(columns={'SETTINGS': 'environment', 'TIMESTAMP': 'timestamp', 'UUID': 'uuid'})

        labels = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_labels.csv'))
        set_labels = labels[['LABELS', 'UUID']].rename(columns={'LABELS': 'label', 'UUID': 'uuid'})

        self.dataset = [
            {
                'name': 'calendar',
                'records': set_calendar
            }, {
                'name': 'label',
                'records': set_labels
            }, {
                'name': 'environment',
                'records': set_settings
            }, {
                'name': 'headset',
                'records': set_headset,
            }]
        self.dataset_length = len(self.dataset[0]['records'])

    def send_dataset(self, dataset_counter: int) -> None:
        if self.operative_mode == 'development':
            self.development_mode(dataset_counter=dataset_counter)
        else:
            self.execution_mode(dataset_counter=dataset_counter)

    def development_mode(self, dataset_counter: int) -> None:
        catch_timestamp = True

        for session_index in range(0, self.dataset_length):
            # Shuffle in order to create non-synchronized records
            random.shuffle(self.dataset)

            # while is_queue_full():
            #     trace('Ingestion queue full..waiting for 50 sec')
            #     sleep(50)

            info_simulation('', '============================ START SESSION ============================', 0)
            for i in range(0, len(self.dataset)):
                if self.dataset[i]['name'] == 'headset':
                    # Read the 22 channels data in the dataset
                    headset_channels = self.dataset[i]['records'].iloc[session_index * 22:session_index * 22 + 22, :] \
                        .to_dict('records')

                    # Shuffle the headset EEG data
                    random.shuffle(headset_channels)

                    for m in range(0, len(headset_channels)):
                        record = headset_channels[m]
                        uuid = record['uuid']
                        channel = record['channel']

                        # Sending a record with a probability of 0.2
                        # In particular, a missing sample can exist if and only if there are no session to monitor
                        if channel in MISSING_SAMPLES and random.random() < 0.2:
                            warning_simulation(uuid, f'Generating a missing sample [channel {channel}]')
                        else:
                            info_simulation(uuid, f'Sending headset EEG data [channel {channel}]', 1)
                            self.send_record(data=record)

                            # In order to get a timestamp in case of testing mode
                            if TESTING_MODE and dataset_counter == 0 and catch_timestamp:
                                save_timestamp()
                                catch_timestamp = False
                else:
                    record = self.dataset[i]['records'].loc[session_index].to_dict()

                    if random.random() < 0.1 and self.dataset[i]["name"] != 'label':
                        warning_simulation(record["uuid"], f'Generating a missing sample [{self.dataset[i]["name"]}]')
                    else:
                        info_simulation(record["uuid"], f'Sending {self.dataset[i]["name"]} data', 1)
                        self.send_record(data=record)

                        # In order to get a timestamp in case of testing mode
                        if TESTING_MODE and dataset_counter == 0 and catch_timestamp:
                            save_timestamp()
                            catch_timestamp = False

            # Send a session very X milliseconds
            sleep(0.5)

    def execution_mode(self, dataset_counter: int) -> None:
        catch_timestamp = True

        for session_index in range(0, self.dataset_length):
            # Shuffle in order to create non-synchronized records
            random.shuffle(self.dataset)

            # while is_queue_full():
            #     trace('Ingestion queue full..waiting for 50 sec')
            #     sleep(50)

            # Counters related to a single session
            missing_channels = 0
            missing_records = 0

            info_simulation('', '============================ START SESSION ============================', 0)
            for i in range(0, len(self.dataset)):
                if self.dataset[i]['name'] == 'headset':
                    # Read the 22 channels data in the dataset
                    headset_channels = self.dataset[i]['records'].iloc[session_index * 22:session_index * 22 + 22, :] \
                        .to_dict('records')

                    # Shuffle the headset EEG data
                    random.shuffle(headset_channels)

                    for m in range(0, len(headset_channels)):
                        record = headset_channels[m]
                        uuid = record['uuid']
                        channel = record['channel']

                        # Sending a record with a probability of 0.2
                        # Counting missing samples if the system is working in monitoring mode
                        if channel in MISSING_SAMPLES and random.random() < 0.2 and not self.monitoring:
                            warning_simulation(uuid, f'Generating a missing sample [channel {channel}]')
                            missing_channels += 1
                        else:
                            info_simulation(uuid, f'Sending headset EEG data [channel {channel}]', 1)
                            self.send_record(data=record)

                            # In order to get a timestamp in case of testing mode
                            if TESTING_MODE and dataset_counter == 0 and catch_timestamp:
                                save_timestamp()
                                catch_timestamp = False
                else:
                    if self.dataset[i]["name"] == 'label':
                        if self.monitoring:
                            record = self.dataset[i]['records'].loc[session_index].to_dict()
                            info_simulation(record["uuid"], f'Sending {self.dataset[i]["name"]} data', 1)
                            self.send_record(data=record)

                            # In order to get a timestamp in case of testing mode
                            if TESTING_MODE and dataset_counter == 0 and catch_timestamp:
                                save_timestamp()
                                catch_timestamp = False
                        else:
                            # Drop the label (it is not needed)
                            pass
                    else:
                        record = self.dataset[i]['records'].loc[session_index].to_dict()

                        # Generate missing sample if and only if there are no session to monitor
                        # otherwise if the session will be discarded because the threshold is not satisfied
                        # the label will be lost
                        if random.random() < 0.1 and not self.monitoring:
                            warning_simulation(record["uuid"],
                                               f'Generating a missing sample [{self.dataset[i]["name"]}]')
                            missing_records += 1
                        else:
                            info_simulation(record["uuid"], f'Sending {self.dataset[i]["name"]} data', 1)
                            self.send_record(data=record)

                            # In order to get a timestamp in case of testing mode
                            if TESTING_MODE and dataset_counter == 0 and catch_timestamp:
                                save_timestamp()
                                catch_timestamp = False

            # Update operative mode phase (execution or monitoring)
            self.check_current_phase(missing_records=missing_records, missing_channels=missing_channels)

            # Send a session very X milliseconds
            sleep(0.5)

    def check_current_phase(self, missing_records: int, missing_channels: int):
        if not self.monitoring:
            if not (missing_records > 0 or missing_channels > self.missing_samples_threshold):
                self.sessions_executed += 1
                trace(f'Complete session sent to the Ingestion System: {self.sessions_executed}')

                if self.sessions_executed == self.execution_window:
                    trace(f'Starting Monitoring Phase...')
                    self.sessions_executed = 0
                    self.monitoring = True
        else:
            self.sessions_monitored += 1
            if self.sessions_monitored == self.monitoring_window:
                trace(f'Monitoring phase ended. Sessions monitored: {self.sessions_monitored}')
                self.sessions_monitored = 0
                self.monitoring = False


if __name__ == '__main__':
    connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'
    info_simulation('', f'Connection to {connection_string}', 2)
    info_simulation('', f'Testing mode: {TESTING_MODE}\n', 2)

    data_sources_sim = DataSourcesSimulation()
    data_sources_sim.read_dataset()

    for j in range(0, DATASET_TO_SEND):
        info_simulation('', f'Sending Dataset #{j + 1}', 0)
        data_sources_sim.send_dataset(dataset_counter=j)
