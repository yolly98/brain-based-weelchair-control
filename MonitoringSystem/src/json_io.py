from flask import Flask, request
from requests import post
from threading import Thread
import logging
import queue


class JsonIO:
    _json_io_instance = None

    @staticmethod
    def get_instance():
        if JsonIO._json_io_instance is None:
            JsonIO._json_io_instance = JsonIO()
        return JsonIO._json_io_instance

    def __init__(self):
        self._app = Flask(__name__)
        self.queue = queue.Queue()

    def listener(self, ip, port):
        self._app.run(host=ip, port=port, debug=False)

    def get_app(self) -> Flask:
        return self._app

    def receive(self, received_json) -> None:
        self.queue.put(received_json, block=True)

    def get_queue(self) -> queue:
        return self.queue

    # used to test the method receive()
    def send(self, json_to_send, connection_string):
        response = post(connection_string + 'json', json=json_to_send)
        if response.status_code != 200:
            return False

        return True


app = JsonIO().get_instance().get_app()
log = logging.getLogger('werkzeug')
log.disabled = True


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    new_thread = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    new_thread.start()

    return {}, 200
