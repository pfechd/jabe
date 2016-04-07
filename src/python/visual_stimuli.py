import numpy as np
import scipy


class VisualStimuli:
    """
    Class used for representing Visual Stimuli data

    The stimuli is read from a .mat file. The data can be accessed through
    the member called data.
    """
    def __init__(self, path, tr):
        self.path = path
        self.tr = tr
        # TODO: Handle loading wrong files
        visual_stimuli_file = scipy.io.loadmat(path)
        visual_stimuli = visual_stimuli_file['visual_stimuli']
        self.amount = visual_stimuli.shape[0]

        self.data = np.zeros((visual_stimuli.shape[0], visual_stimuli.shape[1]))
        self.data[:, 0] = np.floor(visual_stimuli[:, 0] / tr)
        self.data[:, 1] = visual_stimuli[:, 1]


    def get_configuration(self):
        return {
            'stimuli_onset_path': self.path,
            'tr': self.tr
        }
