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

    def test_settings_changed(self):
        ref = Session()

        self.assertFalse(ref.settings_changed(False, False, None, None))
        self.assertTrue(ref.settings_changed(True, False, None, None))

    @unittest.skip('Not finished')
    def test_load_config(self):
        # Crash if session has no name in config
        ref = Session()

        ref.load_configuration({'path': 'test_path',
                                'anatomy_path': 'test_anatomy_path',
                                'name': 'test_name',
                                'description': 'test_desc',
                                'plot_settings': 'test_settings'})

        self.assertEqual(ref.name, 'test_name')
        self.assertEqual(ref.description, 'test_desc')
        self.assertEqual(ref.plot_settings, 'test_settings')

if __name__ == '__main__':
    unittest.main()
