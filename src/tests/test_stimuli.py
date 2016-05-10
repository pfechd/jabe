import unittest
import mock
import scipy.io
from src.stimuli import Stimuli


class TestStimuli(unittest.TestCase):

    @mock.patch('src.stimuli.np')
    @mock.patch('src.stimuli.scipy')
    def test_stimuli(self, mock_scipy, mock_np):
        Stimuli('src/tests/test-data/stimuli.mat', 0.5)
        mock_scipy.io.loadmat.assert_called_with('src/tests/test-data/stimuli.mat')

    def test_get_configuration(self):
        ref = Stimuli('src/tests/test-data/stimuli.mat', 0.5)
        expected = {'path': 'src/tests/test-data/stimuli.mat',
                    'tr': 0.5}
        self.assertEqual(expected, ref.get_configuration())


if __name__ == '__main__':
    unittest.main()