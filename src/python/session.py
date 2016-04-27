# -*- encoding: utf-8 -*-

import numpy as np
import nibabel as nib
from scipy.interpolate import UnivariateSpline
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

        if name:
            self.name = name
        elif configuration:
            self.load_configuration(configuration)
        else:
            raise NotImplementedError('Error not implemented')

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

    def load_data(self, path):
        self.path = path
        self.brain_file = nib.load(path)
        self.sequence = self.brain_file.get_data()
        self.images = self.sequence.shape[3]

    def load_stimuli(self, path, tr):
        self.stimuli = StimuliOnset(path, tr)

    def load_mask(self, mask):
        self.mask = mask

    def calculate_mean(self):
        """ Calculate the mean response """
        mean_responses = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_mean = np.zeros((1, stimuli_data.shape[1]))

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                if rm1[0].any():
                    response_mean[:, i] = np.mean(stimuli_data[rm1[0], i])

            mean_responses[stimuli_type] = response_mean

        return mean_responses

    def calculate_std(self):
        """ Calculate the standard deviation of the response """
        responses_std = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_std = np.zeros((1, stimuli_data.shape[1]))

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                if rm1[0].any():
                    response_std[:, i] = np.std(stimuli_data[rm1[0], i], ddof=1)

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

    def sub_from_baseline(self, response):
        """ Subtract baseline from a response
        :param response: the response to subtract from
        """
        sub_value = response[0]

        for i in range(self.images):
            response[i] -= sub_value

        return response

    def get_voxel_size(self):
        """ Returns the size of one voxel in the image. """
        return self.brain_file._header.get_zooms()

    @staticmethod
    def calculate_fwhm(x, y, smoothing):
        """
        Returns two positions showing the full width half maximum(fwhm) of a given array y.

        Calculates two positions r1 and r2 on the x axis where y'[r1] and y'[r2]
        are equal to half of the maximum value of y where y' is a smoothed version of y.

        :param x: Time axis
        :param y: Value axis, for which fwhm is calculated
        :param smoothing: float. Smoothing factor for y. 0 gives no smoothing.
        :return: Two positions on the x axis.
        """

        half_maximum = (np.max(y) + np.min(y)) / 2
        spline = UnivariateSpline(x, y - half_maximum, s=smoothing)
        roots = spline.roots()
        try:
            assert len(roots) == 2  # Higher smoothing factor required
        except AssertionError:
            print "Smoothed function contains ", len(roots), " roots, 2 required"
            return 0, 1
        r1, r2 = roots
        # DEBUG
        #plt.plot(x, spline(x) + half_maximum)
        return r1, r2

    @staticmethod
    def calculate_amplitude(x, y, smoothing):

        spline = UnivariateSpline(x, y, s=smoothing)  # Remove spline if smoothing is unnecessary
        max_amp = np.argmax(spline(x))
        return max_amp, spline(x)[max_amp]


