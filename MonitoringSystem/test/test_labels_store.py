import os
import json

from src.labels_store import LabelsStore


# ===================== STORE LABEL TEST ===================== #

def test1_insert_label():
    session_label_path = os.path.join(os.path.abspath('..'), 'data', 'session_label_test2.json')
    with open(session_label_path) as f:
        session_label = json.load(f)
    print("uuid to compare :", session_label['uuid'])
    labels_store = LabelsStore()
    labels_store.store_session_label(session_label)


def test2_insert_label():
    session_label_path = os.path.join(os.path.abspath('..'), 'data', 'session_label_test2.json')
    with open(session_label_path) as f:
        session_label = json.load(f)
    print("uuid to compare :", session_label['uuid'])
    labels_store = LabelsStore()
    labels_store.store_session_label(session_label)


def test3_insert_label():
    session_label_path = os.path.join(os.path.abspath('..'), 'data', 'session_label_test3.json')
    with open(session_label_path) as f:
        session_label = json.load(f)
    print("uuid to compare :", session_label['uuid'])
    labels_store = LabelsStore()
    labels_store.store_session_label(session_label)


def test_create_new_row():
    session_label_path = os.path.join(os.path.abspath('..'), 'data', 'session_label_test4.json')
    with open(session_label_path) as f:
        session_label = json.load(f)
    print("uuid to compare :", session_label['uuid'])
    labels_store = LabelsStore()
    labels_store.store_session_label(session_label)


# ===================== LOAD LABEL TEST ===================== #

def test_load_session_label():
    labels_store = LabelsStore()
    labels = labels_store.load_labels()
    print("\nALL LABELS IN THE DB\n")
    print(labels)
    for row in labels:
        print(f"uuid:{row['uuid']}, label1:{row['label1']}, label2:{row['label2']}\n")


# ===================== DELETE LABELS TEST ===================== #
def test_delete_labels():
    labels_store = LabelsStore()
    labels_store.delete_labels()


# ===================== CHECK ROW COMPLETE TEST ===================== #
def test_row_label_complete():
    labels_store = LabelsStore()
    uuid = "a923-45b7-gh12-7408023776.5000"
    res = labels_store.row_label_complete(uuid)
    print("ROW COMPLETE : ", res)
