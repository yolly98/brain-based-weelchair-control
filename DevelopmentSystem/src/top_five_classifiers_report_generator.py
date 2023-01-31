import json
import os
from random import random, choice

from jsonschema import validate, ValidationError

from utility.logging import trace, error


class TopFiveClassifiersReportGenerator:

    def __init__(self) -> None:
        self._json_path = os.path.join(os.path.abspath('..'), 'data', 'top_five_classifiers_report.json')

    def generate_report(self, top_five_classifiers: dict, testing: bool) -> None:
        # if testing mode randomically generate the answers (there is one actual_best with the 80% of probability)
        if testing is True:
            if random() < 0.8:
                # randomically select the actual best
                best = choice(top_five_classifiers['classifiers'])
                best['actual_best'] = True

        # save the report in a JSON file
        with open(self._json_path, "w") as f:
            json.dump(top_five_classifiers, f, indent=4)
        trace('Top Five Classifiers Report exported')

    def evaluate_report(self) -> int:
        # open report and schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'top_five_classifiers_report_schema.json')) as f:
            report_schema = json.load(f)
        with open(self._json_path) as f:
            report = json.load(f)

        # validate the schema
        try:
            validate(report, report_schema)
        except ValidationError:
            error('Top Five Classifiers Report validation failed')
            exit(1)

        best_classifier_uuid = -1       # it will contain the uuid of the best classifier (-1 if there isn't)
        actual_best_counter = 0         # counter to check if more than one classifier is marked as best

        # iterate the classifiers
        for classifier in report['classifiers']:
            if classifier['actual_best'] is True:
                best_classifier_uuid = classifier['uuid']
                actual_best_counter += 1

        # check if more than one classifier is marked as best
        if actual_best_counter > 1:
            error('Only one classifier can be marked as \'actual_best\'')
            exit(1)

        return best_classifier_uuid
