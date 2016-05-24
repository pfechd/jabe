# Copyright (C) 2016 pfechd
#
# This file is part of JABE.
#
# JABE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# JABE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JABE.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import mock
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