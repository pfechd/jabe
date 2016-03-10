import unittest
import matlab.engine
from src.python import mask

class TestBrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = matlab.engine.connect_matlab()
        cls.mask = mask.Mask('../python/tests/test-data/mask1.nii', cls.session)
        cls.session.load_test_data(nargout=0)

    def test_mask_loaded_correctly(self):
        ref = self.session.get_data('mask_ref')
        loaded_mask = self.session.get_data(self.mask.id)
        self.assertEqual(self.session.isequal(ref, loaded_mask), True)

    @classmethod
    def tearDownClass(cls):
        cls.session.clear(nargout=0)
        cls.session.quit()
        cls.mask = None

if __name__ == '__main__':
    unittest.main()