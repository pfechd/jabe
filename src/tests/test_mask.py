import unittest
import numpy as np
import scipy.io as sio
from src.python import mask


class TestBrain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mask = mask.Mask('src/python/tests/test-data/mask.nii')

    def test_mask_loaded_correctly(self):
        expected_mask = sio.loadmat('src/python/tests/test-data/expectedMask.mat')['mask']
        self.assertEqual(np.array_equal(self.mask.data, expected_mask), True)

    @classmethod
    def tearDownClass(cls):
        cls.mask = None


if __name__ == '__main__':
    unittest.main()