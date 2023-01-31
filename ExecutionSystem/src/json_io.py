from flask import Flask, request
from requests import post, exceptions
from threading import Thread

import queue

class JsonIO:

    _instance = None

    def __init__(self):
        """
        Constructor of the JsonIO class.
        """
        self.app = Flask(__name__)
        self._received_json_queue = queue.Queue()

    @staticmethod
    def get_instance():
        """
        Initialize the instance of the JsonIO class.
        :return:
        """
        if JsonIO._instance is None:
            JsonIO._instance = JsonIO()
        return JsonIO._instance

    def listener(self, ip, port):
        """
        Start the listener on the specified IP and port.
        :return: None
        """
        self.app.run(host=ip, port=port, debug=False)

    # -------- SERVER HANDLER --------

    def get_received_json(self):
        """
        Get the first element of the received json queue.
        :return: dict object of the first json in the queue
        """
        return self._received_json_queue.get(block=True)

    def receive(self, received_json):
        """
        When a .json file is received, it is inserted in a queue of .json files.
        :param received_json: dict object that corresponds to the .json file received
        :return: None
        """
        # if the queue is full the thread is blocked
        try:
            self._received_json_queue.put(received_json,block=True)
        except queue.Full:
            print("Full queue exception")
    # -------- CLIENT REQUEST --------

    def send(self, endpoint_ip, endpoint_port, json_to_send) -> bool:
        """
        Send a dict object to an endpoint interface
        :param endpoint_ip: IP of the endpoint
        :param endpoint_port: port of the endpoint
        :param json_to_send: dict object to send
        :return: boolean that represents if the json is correctly sent or not.
        """
        try:
            response = post(f'http://{endpoint_ip}:{endpoint_port}/json', json=json_to_send)

            if response.status_code != 200:
                error_message = response.json()['error']
                print(f'[-] Error: {error_message}')
                return False
        except exceptions.RequestException as e:
            print(f"***JsonIO*** fail in post request: {e}")
            exit(1)
        return True

app = JsonIO.get_instance().app

@app.post('/json')
def post_json():
    """
    Handle the reception of a .json file starting a new thread with the 'receive' function passing the .json file
    received as argument.
    :return: None
    """
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    thread_receive = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    thread_receive.start()

    return {}, 200