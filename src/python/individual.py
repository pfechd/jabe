class Individual:

    def __init__(self, configuration=None):
        if not configuration:
            self.brain = None
            self.stimuli = None
            self.Mask = None
            self.normalization = None
            self.plot = []
            self.name = None
            self.group_name = None
        else:
            pass

    def get_configuration(self):
        pass

    def calculate(self):
        pass

    def plot(self):
        pass
