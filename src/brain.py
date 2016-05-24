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

import nibabel


class Brain:
    """
    Class used for representing and loading brain images.

    Currently only supports NIfTI1. The data is accessible via the member
    `data`.
    """
    def __init__(self, path):
        """
        :param path: The file path to the brain image/sequence.
        """
        self.path = path
        self.brain_file = nibabel.load(path)

    def get_voxel_size(self):
        """ Returns the size of one voxel in the image. """
        return self.brain_file._header.get_zooms()

    @property
    def shape(self):
        return self.brain_file.shape

    @property
    def sequence(self):
        return self.brain_file.get_data()

    @property
    def images(self):
        if self.brain_file.shape < 4:
            return 1
        else:
            return self.brain_file.shape[3]
