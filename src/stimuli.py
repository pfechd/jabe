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
    def __init__(self, path, tr):
        self.path = path
        self.tr = tr
        stimuli_onset_file = scipy.io.loadmat(path)
        stimuli_onset = stimuli_onset_file['visual_stimuli']
        self.amount = stimuli_onset.shape[0]

        self.data = np.zeros((stimuli_onset.shape[0], stimuli_onset.shape[1]))

        # Convert time stamps to image indices
        self.data[:, 0] = np.floor(stimuli_onset[:, 0] / tr)

        self.data[:, 1] = stimuli_onset[:, 1]
        self.data = self.data.astype(int)  # TODO: Ensure value field always integer

    def get_configuration(self):
        return {
            'path': self.path,
            'tr': self.tr
        }
