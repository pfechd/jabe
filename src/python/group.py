from individual import Individual

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

