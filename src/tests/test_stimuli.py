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
import scipy.io
from src.stimuli import Stimuli


class TestStimuli(unittest.TestCase):

    @mock.patch('src.stimuli.np')
    @mock.patch('src.stimuli.scipy')
    def test_stimuli(self, mock_scipy, mock_np):
        Stimuli('src/tests/test-data/stimuli.mat', 0.5)
        mock_scipy.io.loadmat.assert_called_with('src/tests/test-data/stimuli.mat')

    def test_get_configuration(self):
        ref = Stimuli('src/tests/test-data/stimuli.mat', 0.5)
        expected = {'path': 'src/tests/test-data/stimuli.mat',
                    'tr': 0.5}
        self.assertEqual(expected, ref.get_configuration())


if __name__ == '__main__':
    unittest.main()