import numpy as np
import scipy


class Stimuli:
    """
    Class used for representing Stimuli Onset data

    The stimuli is read from a .mat file. The data can be accessed through
    the member called data.
    """
    def __init__(self, path):
        self.path = path
        self.tr = 0.5
        self.stimuli_onset_file = scipy.io.loadmat(path)
        self.stimuli_onset = self.stimuli_onset_file['visual_stimuli']
        self.amount = self.stimuli_onset.shape[0]

    @property
    def data(self):
        data = np.zeros((self.stimuli_onset.shape[0], self.stimuli_onset.shape[1]))

        # Convert time stamps to image indices
        data[:, 0] = np.floor(self.stimuli_onset[:, 0] / self.tr)

        data[:, 1] = self.stimuli_onset[:, 1]
        data = data.astype(int)  # TODO: Ensure value field always integer

        return data

    def get_configuration(self):
        return {
            'path': self.path,
            'tr': self.tr
        }
