import unittest
import numpy as np
import scipy.io as sio
from src.python import stimulionset


class TestBrain(unittest.TestCase):

    def setUp(self):
        self.stimuli = stimulionset.StimuliOnset('src/python/tests/test-data/stimuli.mat', 0.5)

    def test_stimuli_loaded_correctly(self):
        expected_stimuli = sio.loadmat('src/python/tests/test-data/expectedStimuli.mat')['stimuli']
        self.assertEqual(np.array_equal(self.stimuli.data, expected_stimuli), True)

    def test_stimuli_get_configuration(self):
        self.stimuli.path = '/test/testing/something.nii'
        self.stimuli.tr = 3

        expected_config = {'path': '/test/testing/something.nii', 'tr': 3}

        self.assertEqual(self.stimuli.get_configuration(), expected_config)

    def tearDown(self):
        self.stimuli = None


if __name__ == '__main__':
    unittest.main()