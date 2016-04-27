from individual import Individual
import numpy as np


class Group:
    def __init__(self, name=None, configuration=None):
        self.individuals = []
        self.mask = None
        self.stimuli_onset = None
        self.normalization = None
        self.normalize_on = None
        self.plot_settings = []

        if configuration:
            if 'individuals' in configuration:
                for individual_settings in configuration['individuals']:
                    self.individuals.append(Individual(individual_settings))
            if 'name' in configuration:
                self.name = configuration['name']
        elif name:
            self.name = name
        else:
            raise NotImplementedError("Error message not implemented")

    def add_individual(self, individual):
        self.individuals.append(individual)

    def remove_individual(self, individual):
        self.individuals.remove(individual)

    def calculate(self):
        pass

    def plot(self):
        pass

    def get_configuration(self):
        return {
            'name': self.name,
            'individuals': [individual.get_configuration() for individual in self.individuals]
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
        for i in range(len(self.individuals)):
            individual_response = self.individuals[i].calculate_mean()
            for intensity, data in individual_response.iteritems():
                if intensity in self.responses:
                    self.responses[intensity] = np.concatenate((self.responses[intensity], data), axis=0)
                else:
                    self.responses[intensity] = data

    def prepare_for_calculation(self):
        for i in range(len(self.individuals)):
            self.individuals[i].prepare_for_calculation()



