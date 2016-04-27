from individual import Individual
from data import Data
import numpy as np


class Group(Data):
    def __init__(self, name=None, configuration=None):
        super(Group, self).__init__()
        self.mask = None
        self.stimuli_onset = None
        self.normalization = None
        self.normalize_on = None
        self.plot_settings = []

        if configuration:
            if 'individuals' in configuration:
                for individual_settings in configuration['individuals']:
                    self.children.append(Individual(individual_settings))
            if 'name' in configuration:
                self.name = configuration['name']
        elif name:
            self.name = name
        else:
            raise NotImplementedError("Error message not implemented")

    def calculate(self):
        pass

    def plot(self):
        pass

    def get_configuration(self):
        return {
            'name': self.name,
            'individuals': [individual.get_configuration() for individual in self.children]
        }

    def calculate_mean(self):
        """ Calculate the mean response """
        self.combine_individual_responses()

        mean_responses = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_mean = np.zeros((1, stimuli_data.shape[1]))

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                # TODO: Motivate this if-statement
                if len(rm1[0]) > 0:
                    response_mean[:, i] = np.mean(stimuli_data[rm1[0], i])

            mean_responses[stimuli_type] = response_mean
        return mean_responses

    def combine_individual_responses(self):
        self.responses = {}
        for i in range(len(self.children)):
            individual_response = self.children[i].calculate_mean()
            for intensity, data in individual_response.iteritems():
                if intensity in self.responses:
                    self.responses[intensity] = np.concatenate((self.responses[intensity], data), axis=0)
                else:
                    self.responses[intensity] = data


