from sklearn.model_selection import train_test_split
import math
import utility.logging as log


class LearningSessionSetSplitter:

    def __init__(self, config):
        self.segregation_system_config = config

    def generate_training_validation_testing_set(self, dataset):
        # train_test_split function can split the dataset only in two part, so it's needed to execute it
        # again to obtain three sets
        training_size = self.segregation_system_config['training_set_size']
        validation_size = self.segregation_system_config['validation_set_size']
        testing_size = self.segregation_system_config['testing_set_size']

        testing_size = math.floor((testing_size / (1 - training_size)) * 100) / 100
        validation_size = (100 - testing_size * 100) / 100

        training, res = train_test_split(dataset, train_size=training_size)

        if testing_size > validation_size:
            testing, validation = train_test_split(res, train_size=testing_size)
        else:
            validation, testing = train_test_split(res, train_size=validation_size)

        log.info(f"training_size: {len(training)} validation_size: {len(validation)} testing_size: {len(testing)}")

        # return the final dataset composed by the splitted dataset
        return {'training': training, 'validation': validation, 'testing': testing}