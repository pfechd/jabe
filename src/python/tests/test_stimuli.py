import unittest
import matlab.engine
from src.python import visual_stimuli

class TestBrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = matlab.engine.connect_matlab()
        cls.stimuli = visual_stimuli.VisualStimuli('../python/tests/test-data/stimall.mat', 0.5, cls.session)
        cls.session.load_test_data(nargout=0)

    def test_stimuli_loaded_correctly(self):
        ref = self.session.get_data('stimuli_ref')
        loaded_stimuli = self.session.get_data(self.stimuli.id)
        self.assertEqual(self.session.isequal(ref, loaded_stimuli), True)

    @classmethod
    def tearDownClass(cls):
        cls.session.clear(nargout=0)
        cls.session.quit()
        cls.stimuli = None

if __name__ == '__main__':
    unittest.main()