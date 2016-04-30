# -*- encoding: utf-8 -*-

import numpy as np
import nibabel as nib
from scipy.stats import sem
from mask import Mask
from stimulionset import StimuliOnset
from data import Data


class Session(Data):
    """
    Class used for representing and doing calculations with brain data

    The brain data is initially read from a NIfTI-file (.nii) and the original
    data is stored in the member data
    """

    def __init__(self, name=None, configuration=None):
        super(Session, self).__init__()

        if configuration:
            self.load_configuration(configuration)
        elif name:
            self.name = name

    def load_configuration(self, configuration):
        self.name = configuration['name']

        if 'path' in configuration:
            self.load_data(configuration['path'])

        if 'mask' in configuration:
            self.mask = Mask(configuration['mask']['path'])

        if 'stimuli' in configuration:
            self.stimuli = StimuliOnset(configuration['stimuli']['path'],
                                        configuration['stimuli']['tr'])

    def get_configuration(self):
        configuration = {}

        if self.path:
            configuration['path'] = self.path

        if self.mask:
            configuration['mask'] = self.mask.get_configuration()

        if self.stimuli:
            configuration['stimuli'] = self.stimuli.get_configuration()

        if self.name:
            configuration['name'] = self.name

        return configuration

    def calculate_mean(self):
        """
        Calculate the mean of every response grouped by stimuli type

        :return: A dictionary where the key is the stimuli type and the value
                 is the vector containing the mean value for the given time
                 frame.
        """
        mean_responses = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_mean = np.zeros(stimuli_data.shape[1])

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                if rm1[0].any():
                    response_mean[i] = np.mean(stimuli_data[rm1[0], i])

            mean_responses[stimuli_type] = response_mean

        return mean_responses

    def calculate_std(self):
        """ Calculate the standard deviation of the response """
        responses_std = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_std = np.zeros(stimuli_data.shape[1])

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                if rm1[0].any():
                    response_std[i] = np.std(stimuli_data[rm1[0], i], ddof=1)

            responses_std[stimuli_type] = response_std

        return responses_std

    def calculate_sem(self):
        """ Calculate the standard error of the mean (SEM) of the response """
        responses_sem = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_sem = np.zeros(stimuli_data.shape[1])

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                if rm1[0].any():
                    response_sem[i] = sem(stimuli_data[rm1[0], i], ddof=1)

            responses_sem[stimuli_type] = response_sem

        return responses_sem

    def get_voxel_size(self):
        """ Returns the size of one voxel in the image. """
        return self.brain_file._header.get_zooms()

    def aggregate_(self, percentage, global_, mask=None, stimuli=None):
        if not mask:
            mask = self.mask
        if not stimuli:
            stimuli = self.stimuli

        self.apply_mask(mask)
        self.separate_into_responses(stimuli, percentage, global_)

        return self.responses

