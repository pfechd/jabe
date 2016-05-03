# -*- encoding: utf-8 -*-

import numpy as np
import nibabel as nib
from mask import Mask
from stimulionset import StimuliOnset
from group import Group


class Session(Group):
    """
    Class used for representing and doing calculations with brain data

    The brain data is initially read from a NIfTI-file (.nii) and the original
    data is stored in the member data
    """

    def __init__(self, name=None, configuration=None):
        super(Session, self).__init__()

        self.did_global_normalization = False
        self.did_percent_normalization = False
        self.used_mask = None
        self.used_stimuli = None

        if configuration:
            self.load_configuration(configuration)
        elif name:
            self.name = name

    def load_configuration(self, configuration):
        self.name = configuration['name']

        if 'path' in configuration:
            self.load_data(configuration['path'])

        if 'anatomy_path' in configuration:
            self.load_anatomy(configuration['anatomy_path'])

        if 'mask' in configuration:
            self.mask = Mask(configuration['mask']['path'])

        if 'stimuli' in configuration:
            self.stimuli = StimuliOnset(configuration['stimuli']['path'],
                                        configuration['stimuli']['tr'])

    def get_configuration(self):
        configuration = {}

        if self.path:
            configuration['path'] = self.path

        if self.anatomy_path:
            configuration['anatomy_path'] = self.anatomy_path

        if self.mask:
            configuration['mask'] = self.mask.get_configuration()

        if self.stimuli:
            configuration['stimuli'] = self.stimuli.get_configuration()

        if self.name:
            configuration['name'] = self.name

        return configuration

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


    def get_voxel_size(self):
        """ Returns the size of one voxel in the image. """
        return self.brain_file._header.get_zooms()

    def settings_changed(self, percentage, global_, mask, stimuli):
        """
        Given the settings the method returns whether the same settings was
        run in the previous aggregation.
        """
        if not mask:
            mask = self.mask
        if not stimuli:
            stimuli = self.stimuli

        return any([self.did_percent_normalization != percentage,
                    self.did_global_normalization != global_,
                    self.used_mask != mask,
                    self.used_stimuli != stimuli])

    def _aggregate(self, percentage, global_, mask, stimuli):
        """
        Aggregate response data from children with the given settings. Do not
        call this method directly, instead use the `aggregate` method which
        caches the results.

        :return: A dictionary stimuli-values as keys NxM matrices as values
                 where N is the number of stimuli and M is the length of the
                 shortest stimuli.
        """
        if not mask:
            mask = self.mask
        if not stimuli:
            stimuli = self.stimuli

        # Save settings used
        self.did_percent_normalization = percentage
        self.did_global_normalization = global_
        self.used_mask = mask
        self.used_stimuli = stimuli

        self.apply_mask(mask)
        self.separate_into_responses(stimuli, percentage, global_)

        return self.responses

