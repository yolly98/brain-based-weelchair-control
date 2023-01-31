import os
import sqlite3

from utility.logging import *

DB_NAME = "LabelsStore.db"
DB_PATH = os.path.join(os.path.abspath('..'), DB_NAME)


class LabelsStore:

    def __init__(self):
        self._conn = sqlite3.connect(DB_PATH)

    def _open_connection(self):
        if not os.path.exists(DB_PATH):
            warning("LabelsStore - DB does not exist, create the DB")
            return False
        try:
            self._conn = sqlite3.connect(DB_PATH)
        except sqlite3.Error as err:
            error(f'LabelsStore - Sqlite Connection Error: {err}')
            return False
        return True

    def _close_connection(self):
        if self._conn is None:
            return True

        try:
            self._conn.close()
            self._conn = None
        except sqlite3.Error as err:
            error(f"LabelsStore - Sqlite Close connection Error: {err}")
            return False

        return True

    # ==================== STORE SESSION LABEL ====================#
    def store_session_label(self, session_label):
        _uuid = session_label['uuid']
        _label = session_label['label']

        if not self._open_connection():
            return None
        cursor = self._conn.cursor()

        # check if the row already exists
        query = "SELECT * FROM session_labels WHERE uuid = ?"
        res = LabelsStore._check_if_row_exists(self, query, cursor, _uuid)

        # if the row does not exist, create it
        if not res:
            query = "INSERT INTO session_labels (uuid,label1) VALUES (?,?) "
            LabelsStore._create_new_row(self, query, cursor, _uuid, _label)
            return False
        # if the row, insert the label
        else:
            # check which column is empty
            query = 'SELECT label1,label2 FROM session_labels WHERE uuid = ? AND label1 IS NULL OR label2 IS NULL '
            columns = LabelsStore._find_empty_column(self, query, cursor, _uuid)
            # set the value in the empty column
            if columns is not None:
                if columns[0] is None:
                    column_to_set = "label1"
                elif columns[1] is None:
                    column_to_set = "label2"
                query = 'UPDATE session_labels SET ' + column_to_set + ' = ? WHERE uuid = ? '
                LabelsStore._insert_label(self, query, cursor, _uuid, _label)
                return True
            else:
                warning(f"LabelsStore - Row already full\n")
                return False

    def _check_if_row_exists(self, query, cursor, _uuid):
        """
        Method used in store_label()
        return True if the uuid is already in the DB, False Otherwise
        """
        try:
            cursor.execute(query, (_uuid,))
        except sqlite3.Error as err:
            error(f"LabelsStore - Sqlite Execution Error: {err}")
            exit(1)
        res = cursor.fetchone()
        if res is None:
            return False
        else:
            return True

    def _find_empty_column(self, query, cursor, _uuid):
        """
        Method used in store_label().
        Return the column of a specific row where there is a NULL value
        """
        try:
            cursor.execute(query, (_uuid,))
        except sqlite3.Error as err:
            error(f"LabelsStore - Sqlite Execution Error: {err}")

        res = cursor.fetchone()
        return res

    def _insert_label(self, query, cursor, _uuid, _label):
        """
        Method used in store_label()
        Update the row by inserting the received label
        """
        try:
            cursor.execute(query, (_label, _uuid))

        except sqlite3.Error as err:
            error(f"LabelsStore - Sqlite UPDATE Error: {err}")
            return False

        success(f"LabelsStore -  Successfully UPDATE existing row \n")
        self._conn.commit()

    def _create_new_row(self, query, cursor, _uuid, _label):
        """
        method used in store_label().
        Create a new row with the received uuid and label
        """
        try:
            cursor.execute(query, (_uuid, _label))

        except sqlite3.Error as err:
            error(f"LabelsStore - Sqlite INSERT Error: {err}")
            return False

        success(f"LabelsStore - Successfully INSERT new row\n")
        self._conn.commit()

    # ==================== LOAD SESSION LABELS ====================#
    def load_labels(self):
        """
        Takes from the DB all the rows with no null values and return the values of the
        columns label1 and label2 into a list
        """
        if not self._open_connection():
            return None

        cursor = self._conn.cursor()
        query = "SELECT * FROM session_labels WHERE (label1 IS NOT NULL AND label2 IS NOT NULL)"

        try:
            cursor.execute(query)
        except sqlite3.Error as err:
            error(f"LabelsStore -  Error while LOADING session labels: {err}")
            return None

        res = cursor.fetchall()
        if res is None:
            return None

        labels = []
        label = {}
        for row in res:
            label.update({"uuid": row[0]})
            label.update({"label1": row[1]})
            label.update({"label2": row[2]})
            labels.append(label)
            label = {}
        return labels

    # ==================== DELETE SESSION LABELS ====================#
    def delete_labels(self):

        if not self._open_connection():
            return False

        try:
            cursor = self._conn.cursor()
            query = "DELETE FROM session_labels WHERE (label1 IS NOT NULL AND label2 IS NOT NULL)"

            cursor.execute(query)

        except sqlite3.Error as err:
            error(f"Error while DELETING labels from DB: {err}")
            return False

        self._conn.commit()
        info(f"LabelsStore - Labels DELETED from DB ")
        return True

    # ==================== ROW LABEL COMPLETE ====================#
    def row_label_complete(self, uuid):
        if not self._open_connection():
            return None

        cursor = self._conn.cursor()
        query = "SELECT label1,label2 FROM session_labels WHERE uuid = ? AND (label1 IS NOT NULL AND label2 IS NOT NULL)"

        try:
            cursor.execute(query, (uuid,))
        except sqlite3.Error as err:
            error(f"Error to FIND labels: {err}")
            return None

        res = cursor.fetchone()
        if res is None:
            return False
        else:
            return True
