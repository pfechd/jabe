import numpy as np
import scipy


class StimuliOnset:
    """
    Class used for representing Stimuli Onset data

    The stimuli is read from a .mat file. The data can be accessed through
    the member called data.
    """
    def __init__(self, path, tr):
        self.path = path
        self.tr = tr  # TODO: Where should tr be stored?
        # TODO: Handle loading wrong files
        stimuli_onset_file = scipy.io.loadmat(path)
        stimuli_onset = stimuli_onset_file['visual_stimuli']
        self.amount = stimuli_onset.shape[0]

        self.data = np.zeros((stimuli_onset.shape[0], stimuli_onset.shape[1]))

        # Convert time stamps to image indices
        self.data[:, 0] = np.floor(stimuli_onset[:, 0] / tr)

        self.data[:, 1] = stimuli_onset[:, 1]
        self.data = self.data.astype(int)  # TODO: Ensure value field always integer

    def get_configuration(self):
        return {
            'path': self.path,
            'tr': self.tr
        }