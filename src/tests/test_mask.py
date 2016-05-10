import unittest
import mock
import nibabel
from src.mask import Mask


class TestMask(unittest.TestCase):

    @mock.patch('src.mask.nib')
    def test_mask(self, mock_nib):
        Mask('src/tests/test-data/mask.nii')
        mock_nib.load.assert_called_once_with('src/tests/test-data/mask.nii')

    def test_get_configuration(self):
        ref = Mask('src/tests/test-data/mask.nii')
        self.assertEqual({'path': 'src/tests/test-data/mask.nii'}, ref.get_configuration())


if __name__ == '__main__':
    unittest.main()