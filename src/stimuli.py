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

import numpy as np
import scipy


class Stimuli:
    """
    Class used for representing Stimuli Onset data

    The stimuli is read from a .mat file. The data can be accessed through
    the member called data.
    """
    def __init__(self, path):
        self.path = path
        self.tr = 0.5
        self.stimuli_onset_file = scipy.io.loadmat(path)
        self.stimuli_onset = self.stimuli_onset_file['visual_stimuli']
        self.amount = self.stimuli_onset.shape[0]

    @property
    def data(self):
        data = np.zeros((self.stimuli_onset.shape[0], self.stimuli_onset.shape[1]))

        # Convert time stamps to image indices
        data[:, 0] = np.floor(self.stimuli_onset[:, 0] / self.tr)

        data[:, 1] = self.stimuli_onset[:, 1]
        data = data.astype(int)  # TODO: Ensure value field always integer

        return data

    def get_configuration(self):
        return {
            'path': self.path,
            'tr': self.tr
        }
