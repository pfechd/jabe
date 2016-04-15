class Group:
    def __init__(self, configuration=None):
        self.individuals = []
        self.mask = None
        self.stimuli_onset = None
        self.normalization = None
        self.normalize_on = None
        self.plot_settings = []

        #if configuration:

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
            'brain': [brain.get_configuration() for brain in self.brains],
            'mask': self.mask.get_configuration(),
            'normalization': self.normalization,
            'plot_settings': self.plot_settings,
        }

