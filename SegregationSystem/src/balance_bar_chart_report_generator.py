import os
import json
from jsonschema import validate, ValidationError
import matplotlib.pyplot as plt
import random
import utility.logging as log


class BalanceBarChartReportGenerator:

    def __init__(self):
        pass

    def generate_balance_bar_chart(self, dataset):

        labels = ['move', 'left', 'right', 'stop']
        values = [0, 0, 0, 0]

        # prepare data to build the bar chart
        for p_session in dataset:
            ct = p_session['command_thought']
            index = None
            if ct == 'move':
                index = 0
            elif ct == 'left':
                index = 1
            elif ct == 'right':
                index = 2
            elif ct == 'stop':
                index = 3

            values[index] += 1

        plt.bar(labels, values, width=0.4, align='center')
        plt.xlabel('Commands Thought')
        plt.ylabel('Number of Occurrences')
        plt.title(f'Histogram of Commands Thought')
        plt.grid(True)

        # save data just calculated in a dict
        info = dict()
        info['move'] = values[0]
        info['left'] = values[1]
        info['right'] = values[2]
        info['stop'] = values[3]

        # save bar chart in a png image
        chart_path = os.path.join(os.path.abspath('..'), 'data', 'balancing', 'balance_bar_chart.png')
        try:
            plt.savefig(chart_path)
        except:
            log.error('Failure to save the balance bar chart')
            return None

        log.success('Balance bar chart generated')
        return info

    def generate_balancing_report(self, info, testing_mode):

        # if testing_mode is true the human evaluation in the report has to be simulated,
        # otherwise the evaluation has to be empty
        if testing_mode:
            if random.randint(1, 5) == 1:
                info['evaluation'] = 'not balanced'
            else:
                info['evaluation'] = 'balanced'
        else:
            info['evaluation'] = ''

        # save the report in a json file
        report_path = os.path.join(os.path.abspath('..'), 'data', 'balancing', 'balancing_report.json')
        try:
            with open(report_path, "w") as file:
                json.dump(info, file, indent=4)
        except:
            log.error('Failure to save balancing_report.json')
            return False

        log.success('Balancing report generated')
        return True

    def check_balancing_evaluation_from_report(self):

        report_path = os.path.join(os.path.abspath('..'), 'data', 'balancing', 'balancing_report.json')
        schema_path = os.path.join(os.path.abspath('..'), 'schemas', 'balancing_report_schema.json')

        # open bar chart report and validate it
        try:
            with open(report_path) as file:
                report = json.load(file)

            with open(schema_path) as file:
                report_schema = json.load(file)

            validate(report, report_schema)

        except FileNotFoundError:
            log.error('Failure to open balancing_report.json')
            return -2

        except ValidationError:
            log.error('Balancing Report has invalid schema')
            return -2

        # get the evaluation from loaded report
        evaluation = report['evaluation']

        if evaluation == 'not balanced':
            log.warning("Balancing evaluation: Dataset not balanced")
            return -1
        elif evaluation == 'balanced':
            log.warning("Balancing evaluation: Dataset balanced")
            return 0
        else:
            log.warning("Balancing evaluation not done")
            return -2