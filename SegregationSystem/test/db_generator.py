import sqlite3
import os


def db_duplicator():

    db_name = 'segregation.db'
    db_path = os.path.join(os.path.abspath('..'), 'data', db_name)
    conn = None
    if not os.path.exists(db_path):
        print("Sqlite db doesn't exist, the db will be created")
        exit(1)
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Sqlite Connection Error [{e}]")
        exit(1)

    user_id = 0

    query = "SELECT session_id FROM p_session WHERE user_id = ? ORDER BY session_id DESC LIMIT 1"
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))

    res = cursor.fetchone()
    if res is None:
        prepared_session_counter = 0
    else:
        prepared_session_counter = res[0] + 1


    cursor = conn.cursor()
    query = f" SELECT * FROM p_session WHERE user_id = ? LIMIT 100"
    res = cursor.execute(query, (0, ))
    for session in res:
        user_id = session[0]
        session_id = session[1]
        json = session[2]
        session_id = prepared_session_counter + session_id
        query = "INSERT INTO p_session (user_id, session_id, json) \
                               VALUES(?, ?, ?) "
        cursor = conn.cursor()

        cursor.execute(query, (user_id, session_id, json))
        conn.commit()

    conn.close()


def db_generator():
    db_name = 'segregation.db'
    db_path = os.path.join(os.path.abspath('..'), 'data', db_name)
    conn = None
    if not os.path.exists(db_path):
        print("Sqlite db doesn't exist, the db will be created")
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Sqlite Connection Error [{e}]")
        exit(1)

    cursor = conn.cursor()
    query = " \
                CREATE TABLE IF NOT EXISTS p_session ( \
                    user_id integer, \
                    session_id integer, \
                    json blob, \
                    primary key(user_id, session_id) \
                )"

    try:
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Sqlite Execution Error [{e}]")

    conn.close()


if __name__ == '__main__':
    db_duplicator()


