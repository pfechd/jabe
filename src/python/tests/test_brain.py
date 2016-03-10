import unittest
import matlab.engine
from src.python import brain, mask

class TestBrain(unittest.TestCase):
    def setUp(self):
        names = matlab.engine.find_matlab()
        self.session = matlab.engine.connect_matlab(names[0])
        self.brain = brain.Brain('../python/tests/test-data/brain.nii', self.session)
        self.mask = mask.Mask('../python/tests/test-data/mask1.nii', self.session)
        self.session.load_test_data(nargout=0)

    def test_apply_mask(self):
        self.brain.apply_mask(self.mask)
        a = self.session.get_data('apply_mask_ref')
        b = self.session.get_data(self.brain.masked_id)
        self.assertEqual(self.session.isequal(a, b), True)

    def tearDown(self):
        self.session = None
        self.brain = None

if __name__ == '__main__':
    unittest.main()
