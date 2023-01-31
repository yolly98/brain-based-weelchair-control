import json
import os
import uuid

from src.learning_session_store import LearningSessionStore

LABEL_TO_INT = {
    'move': 0,
    'stop': 1,
    'left': 2,
    'right': 3
}

ENVIRONMENT_TO_INT = {
    'indoor': 0,
    'outdoor': 1
}

if __name__ == '__main__':
    with open(os.path.join(os.path.abspath('.'), 'dataset_100.json')) as f:
        dataset = json.load(f)

    db = LearningSessionStore()
    db.store_dataset(dataset)
    data = db.get_training_set()
    print(len(data['training_data']), len(data['training_labels']))
    data = db.get_validation_set()
    print(len(data['validation_data']), len(data['validation_labels']))
    data = db.get_test_set()
    print(len(data['test_data']), len(data['test_labels']))
    db.delete_dataset()
