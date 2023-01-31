import os
import json
import time
from src.json_io import JsonIO

# used to test method receive()
connection_string = 'http://192.168.178.22:5000' + '/'


def test_receive():
    """
    In this data are made n post request to data the receive method of the JsonIO class
    in order to data the correctness of the system
    """
    json_path = os.path.join(os.path.abspath('..'), 'test', 'data', 'session_label_test1.json')
    with open(json_path) as f:
        json_to_send = json.load(f)
    for i in range(0, 20):
        json_to_send['uuid'] = "a923-45b7-gh12-7408003775." + str(i)
        JsonIO.get_instance().send(json_to_send, connection_string)
        time.sleep(0.3)


def test2_receive():
    """
    In this data is made a post request to data the receive method of the JsonIO class
    :return: True if the json is correctly received, Otherwise False
    """

    json_path = os.path.join(os.path.abspath('..'), 'test', 'data', 'session_label_test2.json')
    with open(json_path) as f:
        json_to_send = json.load(f)
    res2 = JsonIO.get_instance().send(json_to_send, connection_string)

    if res2:
        assert True
    else:
        assert False
