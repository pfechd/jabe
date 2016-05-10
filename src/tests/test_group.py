import unittest
import types
import mock
import numpy as np
from src.group import Group


class TestGroup(unittest.TestCase):

    @mock.patch('src.group.Group.load_configuration')
    def test_group(self, mock_load):
        Group('test.json')
        mock_load.assert_called_once_with('test.json')

    @unittest.skip('Not working')
    @mock.patch('src.group.Stimuli')
    def test_load_stimuli(self, mock_stim):
        ref = Group()
        ref.load_stimuli('src/tests/test-data/stimuli.mat', 0.5)

        mock_stim.assert_called_once_with('src/tests/test-data/stimuli.mat', 0.5)

    @mock.patch('src.group.Brain')
    def test_load_anatomy(self, mock_brain):
        ref = Group()
        ref.load_anatomy('src/tests/test-data/mask.nii')

        mock_brain.assert_called_once_with('src/tests/test-data/mask.nii')

    @mock.patch('src.group.Mask')
    def test_load_mask(self, mock_mask):
        ref = Group()
        ref.load_mask('src/tests/test-data/mask.nii')

        mock_mask.assert_called_once_with('src/tests/test-data/mask.nii')

    def test_calculate_amplitude(self):
        fn = lambda x: -x ** 2 + 20 * x
        test_y = [fn(x) for x in range(21)]
        test_x = np.arange(len(test_y))

        x, max_amp = Group.calculate_amplitude(test_x, test_y, 20)

        self.assertEqual(x, 10)
        self.assertEqual(round(max_amp), 100)

    def test_calculate_fwhm(self):
        fn = lambda x: -x ** 2 + 20 * x
        test_y = [fn(x) for x in range(21)]
        test_x = np.arange(len(test_y))

        r1, r2 = Group.calculate_fwhm(test_x, test_y, 20)

        self.assertEqual(fn(r1), 50)
        self.assertEqual(fn(r2), 50)

        fn = lambda x: x ** 3 - 30 * x ** 2 + 200 * x
        test_y = [fn(x) for x in range(23)]
        test_x = np.arange(len(test_y))

        r1, r2 = Group.calculate_fwhm(test_x, test_y, 20)

        self.assertEqual((r1, r2), (0, 1))


if __name__ == '__main__':
    unittest.main()