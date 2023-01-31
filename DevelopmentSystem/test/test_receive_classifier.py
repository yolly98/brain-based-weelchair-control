import pickle
from threading import Thread

from flask import Flask, request
from sklearn.datasets import make_classification


def deploy(received_json):
    # deserialize classifier
    mlp = pickle.loads(received_json['classifier'].encode('ISO-8859-1'))

    # generate sessions
    sessions, _ = make_classification(n_features=(22 * 4) + 1, n_redundant=0)

    prediction = mlp.predict(sessions)
    print(prediction)


app = Flask(__name__)


@app.post('/json')
def handle_post():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    receive_thread = Thread(target=deploy, args=(received_json,))
    receive_thread.start()

    return {}, 200


app.run(host='0.0.0.0', port=6000, debug=True)
