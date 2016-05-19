import unittest
import scipy.io as sio
import numpy as np
from src.python import session, mask


class TestSession(unittest.TestCase):
    def setUp(self):
        self.session = session.Session(name='test')
        self.mask = mask.Mask(path='src/python/tests/test-data/mask.nii')
        self.session.load_sequence('src/python/tests/test-data/brain.nii')
        self.session.load_stimuli('src/python/tests/test-data/stimuli.mat', 0.5)
        self.session.load_mask(self.mask)

    def test_session_loaded_correctly(self):
        expected_brain = sio.loadmat('src/python/tests/test-data/expectedBrain.mat')['brain']
        self.assertEqual(np.array_equal(self.session.data, expected_brain), True)

    def test_apply_mask(self):
        expected_masked = sio.loadmat('src/python/tests/test-data/expectedMaskApplied.mat')['maskApplied']
        r_expected_masked = np.around(expected_masked, decimals=10)

        self.session.apply_mask(self.mask)
        r_masked_data = np.around(self.session.masked_data, decimals=10)

        self.assertEqual(np.array_equal(r_masked_data, r_expected_masked), True)

    def test_seperate_into_responses(self):
        expected_result = np.array([[3.3428559, -0.26702725],
                                    [0.08753572, -2.05907234],
                                    [0.29670448, 0.13803827],
                                    [-0.18024202, 2.66674443],
                                    [0.6247895, 0.73889287],
                                    [0.0, 0.0]])

        self.session.apply_mask(self.mask)
        self.session.separate_into_responses(self.session.stimuli)

        diff = self.session.response - expected_result

        self.assertEqual((diff < 1e-8).all(), True)

    def test_normalize_local(self):
        expected_result = np.array([[0., -3.60988315],
                                    [0., -2.14660806],
                                    [0., -0.15866621],
                                    [0., 2.84698645],
                                    [0., 0.11410337],
                                    [0., 0.]])

        self.session.calculate()

        diff = self.session.response - expected_result

        self.assertEqual((diff < 1e-8).all(), True)

    def test_calculate_mean(self):
        self.session.calculate()

        expected_result = {200: np.array([0.,  0.]), 40: np.array([0.,  0.]),
                           130: np.array([0.,  0.]), 60: np.array([0.,  0.]),
                           70: np.array([0.,  0.])}
        actual_mean = self.session.get_mean()

        for type, value in actual_mean.iteritems():
            diff = value - expected_result[type]

            self.assertEqual((diff < 1e-8).all(), True)

    def test_calculate_std(self):
        self.session.calculate()

        expected_result = np.array([[0., 2.45139786]])
        actual_std = np.around(self.session.calculate_std(), decimals=10)

        diff = actual_std - expected_result

        self.assertEqual((diff < 1e-08).all(), True)

    def test_calculate_sem(self):
        data = np.array([[1], [2], [3]])
        self.session.response = data
        response_sem = self.session.get_sem()
        self.assertEqual(response_sem, [1 / np.sqrt(3)])

    def test_calculate_fwhm(self):
        fn = lambda x: -x ** 2 + 20 * x
        test_y = [fn(x) for x in range(21)]
        test_x = np.arange(len(test_y))

        r1, r2 = self.session.calculate_fwhm(test_x, test_y, 20)

        self.assertEqual(fn(r1), 50)
        self.assertEqual(fn(r2), 50)

        fn = lambda x: x ** 3 - 30 * x ** 2 + 200 * x
        test_y = [fn(x) for x in range(23)]
        test_x = np.arange(len(test_y))

        r1, r2 = self.session.calculate_fwhm(test_x, test_y, 20)

        self.assertEqual((r1, r2), (0, 1))

    def test_calulate_amplitude(self):
        fn = lambda x: -x ** 2 + 20 * x
        test_y = [fn(x) for x in range(21)]
        test_x = np.arange(len(test_y))

        x, max_amp = self.session.calculate_amplitude(test_x, test_y, 20)

        self.assertEqual(x, 10)
        self.assertEqual(round(max_amp), 100)

    def test_get_voxel_size(self):
        expected = (1.0, 1.0, 1.0, 1.0)
        actual = self.session.get_voxel_size()

        self.assertEqual(expected, actual)

    def test_session_get_configuration(self):
        expected = {
            'path': 'src/python/tests/test-data/brain.nii',
            'stimuli': {'path': 'src/python/tests/test-data/stimuli.mat', 'tr': 0.5},
            'mask': {'path': 'src/python/tests/test-data/mask.nii'},
            'name': 'test'
        }

        actual = self.session.get_configuration()

        self.assertEqual(expected, actual)

    def tearDown(self):
        self.session = None
        self.mask = None


if __name__ == '__main__':
    unittest.main()
