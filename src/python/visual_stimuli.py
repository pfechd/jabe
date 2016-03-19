import numpy as np
import scipy

class VisualStimuli:
    def __init__(self, path, tr):
        self.path = path
        visual_stimuli_file = scipy.io.loadmat(path) # Trivialt
        visual_stimuli = visual_stimuli_file['visual_stimuli']
        self.amount = visual_stimuli.shape[0]

        self.data = np.floor(visual_stimuli[:,0] / tr)
        self.data = np.array([self.data, visual_stimuli[:,1]])
