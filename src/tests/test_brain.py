import unittest
import mock
from src.brain import Brain


class TestBrain(unittest.TestCase):

    @mock.patch('src.brain.nibabel')
    def test_brain(self, mock_nib):
        Brain('src/tests/test-data/brain.nii')
        mock_nib.load.assert_called_with('src/tests/test-data/brain.nii')

    def test_get_voxel_size(self):
        ref = Brain('src/tests/test-data/brain.nii')
        self.assertEqual((1.0, 1.0, 1.0, 1.0), ref.get_voxel_size())


if __name__ == '__main__':
    unittest.main()