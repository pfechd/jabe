from session import Session
from mask import Mask
from stimulionset import StimuliOnset
from plotWindow import CustomPlot


class Individual:

    def __init__(self, configuration=None):
        self.brain = None
        self.stimuli_onset = None
        self.mask = None
        self.normalization = None
        self.plot_settings = []
        self.name = None
        self.group_name = None

        if configuration:
            if 'brain' in configuration:
                self.brain = Session(configuration['brain']['path'])

            if 'mask' in configuration:
                self.mask = Mask(configuration['mask']['path'])

            if 'stimuli_onset' in configuration:
                path = configuration['stimuli_onset']['path']
                tr = configuration['stimuli_onset']['tr']

                self.stimuli_onset = StimuliOnset(path, tr)

            if 'name' in configuration:
                self.name = configuration['name']

    def get_configuration(self):
        configuration = {
            'normalization': self.normalization,
            'plot_settings': self.plot_settings,
            'name': self.name,
            'group_name': self.group_name
        }

        if self.brain:
            configuration['brain'] = self.brain.get_configuration()

        if self.mask:
            configuration['mask'] = self.mask.get_configuration()

        if self.stimuli_onset:
            configuration['stimuli_onset'] = self.stimuli_onset.get_configuration()

        return configuration

    def ready_for_calculation(self):
        return all([self.brain, self.stimuli_onset, self.mask])

    def calculate(self):
        # Check for the data needed for data extraction
        if not self.brain:
            self.brain = Session("test-data/brain_exp1_1.nii")
        if not self.mask:
            self.mask = Mask("test-data/mask.nii")
        if not self.stimuli_onset:
            self.stimuli_onset = StimuliOnset("test-data/stimall.mat", 0.5)

        # Check if dimensions of 'Session' and 'Mask' match.
        if self.brain.data.shape[0:3] != self.mask.data.shape:
            return 'Session image dimensions does not match Mask dimensions\n\nSession: ' \
                   + str(self.brain.data.shape[0:3]) + '\nMask: ' + str(self.mask.data.shape)
        else:
            self.brain.apply_mask(self.mask)
            self.brain.normalize_to_mean(self.stimuli_onset)

    def plot(self):
        pass
