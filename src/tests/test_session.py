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

<<<<<<< HEAD
        ref.load_configuration({'path': 'test_path',
                                'anatomy_path': 'test_anatomy_path',
                                'name': 'test_name',
                                'description': 'test_desc',
                                'plot_settings': 'test_settings'})
=======
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
>>>>>>> master

        self.assertEqual(ref.name, 'test_name')
        self.assertEqual(ref.description, 'test_desc')
        self.assertEqual(ref.plot_settings, 'test_settings')

if __name__ == '__main__':
    unittest.main()
