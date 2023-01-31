import json
import os
from time import sleep

from requests import post

if __name__ == '__main__':
    with open(os.path.join(os.path.abspath('.'), 'dataset_300.json')) as f:
        dataset = json.load(f)

    sleep(5)
    i = 0
    while True:
        post('http://localhost:5000/json', json=dataset)
        print(f'[+] sent dataset {i}')
        i += 1
        sleep(4)
