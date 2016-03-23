import unittest
import matlab.engine
from src.python import brain, mask

class TestBrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = matlab.engine.connect_matlab()
        cls.brain = brain.Brain('../python/tests/test-data/brain.nii', cls.session)
        cls.mask = mask.Mask('../python/tests/test-data/mask1.nii', cls.session)
        cls.session.load_test_data(nargout=0)

    def test_brain_loaded_correctly(self):
        ref = self.session.get_data('brain_ref')
        loaded_brain = self.session.get_data(self.brain.id)
        self.assertEqual(self.session.isequal(ref, loaded_brain), True)

    def test_apply_mask(self):
        self.brain.apply_mask(self.mask)
        ref = self.session.get_data('apply_mask_ref')
        brain_masked = self.session.get_data(self.brain.masked_id)
        self.assertEqual(self.session.isequal(ref, brain_masked), True)

    def test_calculate_mean(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.session.clear(nargout=0)
        cls.brain = None
        cls.mask = None
        cls.session.quit()

if __name__ == '__main__':
    unittest.main()
