import json
import os

from requests import post

def deployment_simulation():
    path = os.path.join(os.path.abspath('..'), 'classifier.json')
    print(path)
    with open(path, 'r') as f:
        classifier = json.load(f)
        print(classifier)
    post("http://127.0.0.1:5000/json", json=classifier)

def execution_simulation():
    path = os.path.join(os.path.abspath('..'), 'prepared_session_execution.json')
    print(path)
    with open(path, 'r') as f:
        session = json.load(f)
        print(session)
    post("http://127.0.0.1:5000/json", json=session)
if __name__ == '__main__':
    deployment_simulation()
    #execution_simulation()
