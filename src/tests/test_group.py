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
import numpy as np
from src.group import Group
from src.session import Session


class TestGroup(unittest.TestCase):

    @mock.patch('src.group.Group.load_configuration')
    def test_group(self, mock_load):
        Group('test.json')
        mock_load.assert_called_once_with('test.json')

    @unittest.skip('Not working')
    @mock.patch('src.group.Stimuli')
    def test_load_stimuli(self, mock_stim):
        ref = Group()
        ref.load_stimuli('src/tests/test-data/stimuli.mat', 0.5)

        mock_stim.assert_called_once_with('src/tests/test-data/stimuli.mat', 0.5)

    @mock.patch('src.group.Brain')
    def test_load_anatomy(self, mock_brain):
        ref = Group()
        ref.load_anatomy('src/tests/test-data/mask.nii')

        mock_brain.assert_called_once_with('src/tests/test-data/mask.nii')

    @mock.patch('src.group.Mask')
    def test_load_mask(self, mock_mask):
        ref = Group()
        ref.load_mask('src/tests/test-data/mask.nii')

        mock_mask.assert_called_once_with('src/tests/test-data/mask.nii')

    @mock.patch('src.group.Group._aggregate', autospec=True)
    @mock.patch('src.group.Group.settings_changed', autospec=True)
    def test_aggregate(self, mock_sett_change, mock_aggr):
        ref = Group()
        ref.aggregate()
        mock_sett_change.assert_called_once_with(ref, None, None, None, None)
        mock_aggr.assert_called_once_with(ref, None, None, None, None)

    def test_add_children(self):
        ref = Group()
        child1 = Session()
        child2 = Session()

        ref.add_child(child1)
        ref.add_child(child2)

        self.assertEqual([child1, child2], ref.children)

    def test_remove_children(self):
        ref = Group()
        child1 = Session()
        child2 = Session()

        ref.add_child(child1)
        ref.add_child(child2)

        ref.remove_child(child1)

        self.assertEqual([child2], ref.children)

    def test_load_config(self):
        ref = Group()

        ref.load_configuration({'name': 'test_name',
                                'description': 'test_desc',
                                'plot_settings': 'test_settings'})

        self.assertEqual(ref.name, 'test_name')
        self.assertEqual(ref.description, 'test_desc')
        self.assertEqual(ref.plot_settings, 'test_settings')

    def test_calculate_amplitude(self):
        fn = lambda x: -x ** 2 + 20 * x
        test_y = [fn(x) for x in range(21)]
        test_x = np.arange(len(test_y))

        x, max_amp = Group.calculate_amplitude(test_x, test_y, 20)

        self.assertEqual(x, 10)
        self.assertEqual(round(max_amp), 100)

    def test_calculate_fwhm(self):
        fn = lambda x: -x ** 2 + 20 * x
        test_y = [fn(x) for x in range(21)]
        test_x = np.arange(len(test_y))

        r1, r2 = Group.calculate_fwhm(test_x, test_y, 20)

        self.assertEqual(fn(r1), 50)
        self.assertEqual(fn(r2), 50)

        fn = lambda x: x ** 3 - 30 * x ** 2 + 200 * x
        test_y = [fn(x) for x in range(23)]
        test_x = np.arange(len(test_y))

        r1, r2 = Group.calculate_fwhm(test_x, test_y, 20)

        self.assertEqual((r1, r2), (0, 1))



if __name__ == '__main__':
    unittest.main()