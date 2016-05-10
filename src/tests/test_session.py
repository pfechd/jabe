import unittest
import mock
from src.session import Session


class TestSession(unittest.TestCase):

    @mock.patch('src.session.Session.load_configuration')
    def test_session(self, mock_load):
        Session('test.json')
        mock_load.assert_called_once_with('test.json')

    @mock.patch('src.session.Brain')
    def test_load_anatomy(self, mock_brain):
        ref = Session()
        ref.load_sequence('src/tests/test-data/brain.nii')

        mock_brain.assert_called_once_with('src/tests/test-data/brain.nii')

    def test_get_configuration(self):
        ref = Session()
        ref.load_sequence('src/tests/test-data/brain.nii')
        ref.load_anatomy('src/tests/test-data/mask.nii')
        ref.load_stimuli('src/tests/test-data/stimuli.mat', 0.5)

        expected = {'path': 'src/tests/test-data/brain.nii',
                    'stimuli': {'path': 'src/tests/test-data/stimuli.mat', 'tr': 0.5},
                    'anatomy_path': 'src/tests/test-data/mask.nii'}

        self.assertEqual(ref.get_configuration(), expected)



if __name__ == '__main__':
    unittest.main()
