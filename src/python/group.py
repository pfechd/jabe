class Group:

    def __init__(self, configuration=None):
        if not configuration:
            self.brains = []
            self.mask = None
            self.stimuli_onset = None
            self.normalization = None
            self.normalize_on = None
            self.plot = []
        else:
            pass

    def calculate(self):
        pass

    def plot(self):
        pass

    def get_configuration(self):
        pass
