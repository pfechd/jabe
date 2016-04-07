class Individual:

    def __init__(self, configuration=None):
        if not configuration:
            self.brain = None
            self.stimuli = None
            self.mask = None
            self.normalization = None
            self.plot_settings = []
            self.name = None
            self.group_name = None
        else:
            pass

    def get_configuration(self):
        return {
            'brain': self.brain.get_configuration(),
            'mask': self.mask.get_configuration(),
            'normalization': self.normalization,
            'plot_settings': self.plot_settings,
            'name': self.name,
            'group_name': self.group_name
        }

    def calculate(self):
        pass

    def plot(self):
        pass
