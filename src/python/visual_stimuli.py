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
        # TODO: Handle loading wrong files
        visual_stimuli_file = scipy.io.loadmat(path)
        visual_stimuli = visual_stimuli_file['visual_stimuli']
        self.amount = visual_stimuli.shape[0]

        self.data = np.floor(visual_stimuli[:, 0] / tr)
        self.data = np.array([self.data, visual_stimuli[:, 1]])
