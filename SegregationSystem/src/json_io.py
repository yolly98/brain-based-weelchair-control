from flask import Flask, request
from requests import post, exceptions
import queue
import utility.logging as log


class JsonIO:

    _instance = None

    def __init__(self):
        # Flask instance to receive data
        self._app = Flask(__name__)
        # a thread-safe queue to buffer the received json message
        self._received_json_queue = queue.Queue()

    @staticmethod
    def get_instance():
        if JsonIO._instance is None:
            JsonIO._instance = JsonIO()
        return JsonIO._instance

    def listener(self, ip, port):
        # execute the listening server, for each message received, it will be handled by a thread
        self._app.run(host=ip, port=port, debug=False, threaded=True)

    def get_app(self):
        return self._app

    def receive(self):
        # get json message from the queue
        # if the queue is empty the thread is blocked
        return self._received_json_queue.get(block=True)

    def put_json_into_queue(self, received_json):
        # save received message into queue
        self._received_json_queue.put(received_json)

    def send(self, ip, port, data):
        connection_string = f'http://{ip}:{port}/json'
        response = None
        try:
            response = post(connection_string, json=data)
        except exceptions.RequestException:
            log.error("Endpoint system unreachable")
            return False

        if response.status_code != 200:
            res = response.json()
            error_message = 'unknown'
            if 'error' in res:
                error_message = res['error']
            log.error(f'Sending Error: {error_message}')
            return False

        return True


app = JsonIO.get_instance().get_app()


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json
    JsonIO.get_instance().put_json_into_queue(received_json)
    return {}, 200