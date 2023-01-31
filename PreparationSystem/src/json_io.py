import queue
from threading import Thread

from flask import Flask, request
from requests import post, exceptions


class JsonIO:
    """
    JsonIO is a class that provides functionality for sending and receiving JSON payloads.
    It uses Flask to handle incoming JSONs and the requests library to send them to other endpoints.
    """
    json_io_instance = None

    def __init__(self):
        """
        Initializes a new JsonIO instance and creates a Flask application and a queue for storing
        received JSON payloads.
        """
        self.app = Flask(__name__)
        self._received_json_queue = queue.Queue()

    def listener(self, ip, port):
        """
        Starts the listener on the specified IP and port.
        :param ip: IP address to listen on.
        :param port: Port to listen on.
        :return: None
        """
        self.app.run(host=ip, port=port, debug=False)

    def get_received_json(self):
        """
        Retrieves a raw session from the received JSON queue.
        :return: Raw session
        """
        return self._received_json_queue.get(block=True)

    # -------- SERVER HANDLER --------

    def receive(self, received_json):
        """
        Adds the received JSON payload to _received_json_queue.
        :param received_json: JSON payload received by the server.
        :return: None
        """
        # If the queue is full the thread is blocked
        try:
            self._received_json_queue.put(received_json, timeout=5)
        except queue.Full:
            print("Full queue exception")

    # -------- CLIENT REQUEST --------

    def send(self, endpoint_ip: str, endpoint_port: int, json_to_send: dict):
        """
        Sends a JSON payload to a specified endpoint.
        :param endpoint_ip: The IP address of the endpoint.
        :param endpoint_port: The port of the endpoint.
        :param json_to_send: The JSON payload to send.
        :return: True if the payload is sent successfully, False otherwise.
        """
        try:
            response = post(f'http://{endpoint_ip}:{endpoint_port}/json', json=json_to_send, timeout=5)
            if response.status_code != 200:
                error_message = response.json()['error']
                print(f'[-] Error: {error_message}')
                return False
        except exceptions.RequestException as e:
            print(f'[-] Connection Error (endpoint unreachable): {e}')
            exit(1)
        return True

    @staticmethod
    def get_instance():
        """
        :return: Instance of the JsonIO class
        """
        if JsonIO.json_io_instance is None:
            JsonIO.json_io_instance = JsonIO()
        return JsonIO.json_io_instance


app = JsonIO.get_instance().app


@app.post('/json')
def post_json():
    """
    The function is called when a post request is received on the json endpoint.
    :return: Returns a JSON response with status code 200 if the request is successful,
            and with status code 500 if it's not.
    """
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    new_thread = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    new_thread.start()

    return {}, 200
