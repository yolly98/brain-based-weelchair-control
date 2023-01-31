import json
import os
import sqlite3
import uuid

from jsonschema import validate, ValidationError

from utility.logging import error, trace, success, warning

# labels to integer conversion
LABEL_TO_INT = {
    'move': 0,
    'stop': 1,
    'left': 2,
    'right': 3
}

# environment to integer conversion
ENVIRONMENT_TO_INT = {
    'indoor': 0,
    'outdoor': 1
}


class LearningSessionStore:

    def __init__(self) -> None:
        self._conn = sqlite3.connect(os.path.join(os.path.abspath('..'), 'data', 'learning_session_store.db'))

        if self._conn is not None and self._create_table():
            trace('Connection to DB established and \'learning_session\' table initialized')
        else:
            error('Failed to initialize learning session store')
            exit(1)

    def _check_connection(self) -> bool:
        return self._conn is not None

    def _create_table(self) -> bool:
        if self._check_connection() is False:
            return False

        # generate all column names
        channels = ['ALPHA', 'BETA', 'DELTA', 'THETA']
        column_names = []
        for channel in channels:
            for i in range(22):
                column_names.append(f'{channel}_{i}')
        column_names.append('ENVIRONMENT')
        column_names.append('LABEL')

        try:
            # create the base of the query
            query = '(UUID TEXT PRIMARY KEY UNIQUE'
            for column_name in column_names:
                query += ', ' + column_name + ' INTEGER'
            query += ');'

            # create the three tables
            for table_name in ['training_set', 'validation_set', 'test_set']:
                new_query = 'CREATE TABLE IF NOT EXISTS ' + table_name + query
                self._conn.cursor().execute(new_query)
                self._conn.commit()

        except sqlite3.Error:
            error('Failed to create table')
            return False

        return True

    def _insert_dataset(self, dataset: list, dataset_name: str) -> bool:
        try:
            query = 'INSERT INTO ' + dataset_name + ' VALUES (?' + (',?' * (22 * 4 + 2)) + ')'
            self._conn.cursor().executemany(query, dataset)
            self._conn.commit()
        except sqlite3.Error:
            error(f'Failed to insert {dataset_name} dataset')
            return False

        success(f'Inserted new dataset in the \'{dataset_name}\' table')
        return True

    def store_dataset(self, received_dataset: dict) -> bool:
        # open schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'received_dataset_schema.json')) as f:
            received_dataset_schema = json.load(f)

        # validate the config
        try:
            validate(received_dataset, received_dataset_schema)
        except ValidationError:
            warning('Received Dataset validation failed')
            return False

        # convert training set to a list of tuple
        training = []
        for session in received_dataset['training']:
            session = [str(uuid.uuid4())] + session['features']['alpha'] + session['features']['beta'] + \
                      session['features']['delta'] + session['features']['theta'] + \
                      [ENVIRONMENT_TO_INT[session['features']['environment']],
                       LABEL_TO_INT[session['command_thought']]]
            training.append(tuple(session))

        # convert validation set to a list of tuple
        validation = []
        for session in received_dataset['validation']:
            session = [str(uuid.uuid4())] + session['features']['alpha'] + session['features']['beta'] + \
                      session['features']['delta'] + session['features']['theta'] + \
                      [ENVIRONMENT_TO_INT[session['features']['environment']],
                       LABEL_TO_INT[session['command_thought']]]
            validation.append(tuple(session))

        # convert test set to a list of tuple
        test = []
        for session in received_dataset['testing']:
            session = [str(uuid.uuid4())] + session['features']['alpha'] + session['features']['beta'] + \
                      session['features']['delta'] + session['features']['theta'] + \
                      [ENVIRONMENT_TO_INT[session['features']['environment']],
                       LABEL_TO_INT[session['command_thought']]]
            test.append(tuple(session))

        # insert the three datasets in the database
        res_training = self._insert_dataset(training, 'training_set')
        res_validation = self._insert_dataset(validation, 'validation_set')
        res_test = self._insert_dataset(test, 'test_set')

        if res_training and res_validation and res_test:
            return True
        return False

    def delete_dataset(self) -> bool:
        try:
            # empty the three tables
            for table_name in ['training_set', 'validation_set', 'test_set']:
                query = 'DELETE FROM ' + table_name
                self._conn.cursor().execute(query)
                self._conn.commit()
        except sqlite3.Error:
            error('Failed to empy dataset')
            return False

        trace(f'The dataset has been removed from DB')
        return True

    def get_training_set(self) -> dict:
        dataset = self._get_dataset('training_set')
        return {'training_data': dataset[0], 'training_labels': dataset[1]}

    def get_validation_set(self) -> dict:
        dataset = self._get_dataset('validation_set')
        return {'validation_data': dataset[0], 'validation_labels': dataset[1]}

    def get_test_set(self) -> dict:
        dataset = self._get_dataset('test_set')
        return {'test_data': dataset[0], 'test_labels': dataset[1]}

    def _get_dataset(self, dataset_name: str) -> list:
        try:
            results = []

            # generate all column names
            channels = ['ALPHA', 'BETA', 'DELTA', 'THETA']
            column_names = []
            for channel in channels:
                for i in range(22):
                    column_names.append(f'{channel}_{i}')
            column_names.append('ENVIRONMENT')

            cursor = self._conn.cursor()

            # get the features
            query = f'SELECT {", ".join(column_names)} FROM {dataset_name}'
            cursor.execute(query)
            results.append(cursor.fetchall())

            # get the labels
            query = f'SELECT LABEL FROM {dataset_name}'
            cursor.execute(query)
            results.append(cursor.fetchall())
        except sqlite3.Error:
            error(f'Failed to get datset from DB')
            return None

        return results
