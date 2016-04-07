import unittest
import scipy.io as sio
import numpy as np
from src.python import brain, mask, visual_stimuli


class TestBrain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.brain = brain.Brain('src/python/tests/test-data/brain.nii')
        cls.mask = mask.Mask('src/python/tests/test-data/mask.nii')
        cls.stimuli = visual_stimuli.VisualStimuli('src/python/tests/test-data/stimuli.mat', 0.5)

    def test_brain_loaded_correctly(self):
        expected_brain = sio.loadmat('src/python/tests/test-data/expectedBrain.mat')['brain']
        self.assertEqual(np.array_equal(self.brain.data, expected_brain), True)

    def test_apply_mask(self):
        expected_masked = sio.loadmat('src/python/tests/test-data/expectedMaskApplied.mat')['maskApplied']
        r_expected_masked = np.around(expected_masked, decimals=10)

        self.brain.apply_mask(self.mask)
        r_masked_data = np.around(self.brain.masked_data, decimals=10)

        self.assertEqual(np.array_equal(r_masked_data, r_expected_masked), True)

    def test_normalize_to_mean(self):
        expected_norm_to_mean = sio.loadmat('src/python/tests/test-data/expectedNormToMean')['normToMean']
        r_expected_norm_to_mean = np.around(expected_norm_to_mean, decimals=10)

        self.brain.normalize_to_mean(self.stimuli)
        r_norm_to_mean = np.around(self.brain.response, decimals=10)

        self.assertEqual(r_expected_norm_to_mean.shape, r_norm_to_mean.shape)

    def test_calculate_mean(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.brain = None
        cls.mask = None


if __name__ == '__main__':
    unittest.main()
