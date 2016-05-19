# -*- encoding: utf-8 -*-

import numpy as np
import nibabel as nib
from mask import Mask
from src.brain import Brain
from stimuli import Stimuli
from group import Group


class Session(Group):
    """
    Class used for representing and doing calculations with brain data

    The brain data is initially read from a NIfTI-file (.nii) and the original
    data is stored in the member data
    """

    def __init__(self, configuration=None):
        super(Session, self).__init__()

        self.brain = None
        self.masked_data = None
        self.did_global_normalization = False
        self.did_percent_normalization = False
        self.used_mask = None
        self.used_stimuli = None

        if configuration:
            self.load_configuration(configuration)

    def load_configuration(self, configuration):
        if 'name' in configuration:
            self.name = configuration['name']

        if 'description' in configuration:
            self.description = configuration['description']

        if 'plot_settings' in configuration:
            self.plot_settings = configuration['plot_settings']

        if 'path' in configuration:
            self.load_sequence(configuration['path'])

        if 'anatomy_path' in configuration:
            self.load_anatomy(configuration['anatomy_path'])

        if 'mask' in configuration:
            self.load_mask(configuration['mask']['path'])

        if 'stimuli' in configuration:
            self.load_stimuli(configuration['stimuli']['path'],
                                   configuration['stimuli']['tr'])

    def get_configuration(self):
        configuration = {}

        if self.brain:
            configuration['path'] = self.brain.path

        if self.anatomy:
            configuration['anatomy_path'] = self.anatomy.path

        if self.mask:
            configuration['mask'] = self.mask.get_configuration()

        if self.stimuli:
            configuration['stimuli'] = self.stimuli.get_configuration()

        if self.name:
            configuration['name'] = self.name

        if self.description:
            configuration['description'] = self.description

        if self.plot_settings:
            configuration['plot_settings'] = self.plot_settings

        return configuration

    def ready_for_calculation(self, stimuli=None, mask=None):
        return self.brain is not None and \
               super(Session, self).ready_for_calculation(stimuli, mask)

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
        self.separate_into_responses(stimuli)
        self.normalize(percentage, global_)

        return self.responses

    def separate_into_responses(self, stimuli):
        number_of_stimuli = stimuli.amount

        shortest_interval = min([j - i for i, j in zip(stimuli.data[:-1, 0], stimuli.data[1:, 0])])

        self.responses = {}

        # Ignore the images after the last time stamp
        for i in range(number_of_stimuli - 1):
            start = stimuli.data[i, 0]
            end = start + shortest_interval
            response = self.masked_data[:, (start - 1):(end - 1)]
            intensity = str(stimuli.data[i, 1])
            if intensity in self.responses:
                self.responses[intensity] = np.concatenate((self.responses[intensity], response))
            else:
                self.responses[intensity] = response

    def apply_mask(self, mask):
        """
        Apply the given mask to the brain and save the data for further
        calculations in the member masked_data.

        :param mask: Mask object which should be applied
        """
        self.masked_data = np.zeros((1, self.brain.images))

        for i in range(self.brain.images):
            visual_brain = mask.data * self.brain.sequence[:, :, :, i]
            visual_brain_time = np.nonzero(visual_brain)
            self.masked_data[:, i] = np.mean(visual_brain[visual_brain_time])

    def normalize(self, percentage, global_):
        """
        Normalizes all sequences in the session

        Assumes all values in self.responses are non-zero.
        Assumes that there exists non-zero values in self.brain.sequence.
        :param percentage: Whether percentual change from reference value should be shown.
        If false, the response will be normalized by subtraction of the reference value.
        :param global_: Whether reference value should be the global mean.
        If false, reference value will be the start value of the response
        """
        if global_:
            ref = np.sum(self.brain.sequence, (0, 1, 2, 3))     # Sum of all dimensions
            number_of_samples = np.nonzero(self.brain.sequence)[0].size     # Count the coordinates
            ref = ref / number_of_samples

        for key in self.responses.keys():
            number_of_stimuli = self.responses[key].shape[0]

            if global_:
                ref = np.ones(number_of_stimuli) * ref
            else:
                ref = self.responses[key][:, 0]
            for i in range(number_of_stimuli):
                if percentage:
                    self.responses[key][i, :] = (self.responses[key][i, :] / ref[i]) * 100
                else:
                    self.responses[key][i, :] = self.responses[key][i, :] - ref[i]

    def load_sequence(self, path):
        """ Load the sequence from the path. Returns an error message if something went wrong, otherwise None """
        try:
            temp_brain = Brain(path)
        except IOError:
            return path + " does not exist"
        except:
            return path + " could not be opened. It might be corrupted"
        if len(temp_brain.shape) != 4:
            return "The data has " + str(len(temp_brain.shape)) + " dimensions instead of 4"
        elif self.mask and self.mask.shape != temp_brain.shape[0:3]:
            return "The EPI sequence is not the same size as the mask"
        elif self.stimuli and self.stimuli.data[-1,0] > temp_brain.images:
            return "The EPI sequence is too short compared to the times in the stimuli file"
        else:
            self.brain = temp_brain
            return None
