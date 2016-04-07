import unittest
import numpy as np
import scipy.io as sio
from src.python import visual_stimuli


class TestBrain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.stimuli = visual_stimuli.VisualStimuli('src/python/tests/test-data/stimuli.mat', 0.5)

    def test_stimuli_loaded_correctly(self):
        expected_stimuli = sio.loadmat('src/python/tests/test-data/expectedStimuli.mat')['stimuli']
        self.assertEqual(np.array_equal(self.stimuli.data, expected_stimuli), True)

    @classmethod
    def tearDownClass(cls):
        cls.stimuli = None


if __name__ == '__main__':
    unittest.main()