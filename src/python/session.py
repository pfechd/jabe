# -*- encoding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
from scipy.interpolate import UnivariateSpline
from scipy.stats import sem
from mask import Mask
from stimulionset import StimuliOnset


class Session:
    """
    Class used for representing and doing calculations with brain data

    The brain data is initially read from a NIfTI-file (.nii) and the original
    data is stored in the member data
    """

    def __init__(self, name=None, configuration=None):
        self.path = None
        self.brain_file = None
        self.data = None
        self.images = None
        self.masked_data = None
        self.response = None
        self.stimuli = None
        self.mask = None

        if name:
            self.name = name
        elif configuration:
            self.name = configuration['name']

            if 'path' in configuration:
                self.load_data(configuration['path'])

            if 'mask' in configuration:
                self.mask = Mask(configuration['mask']['path'])

            if 'stimuli' in configuration:
                self.stimuli = StimuliOnset(configuration['stimuli']['path'],
                                            configuration['stimuli']['tr'])
        else:
            raise NotImplementedError('Error not implemented')

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
        self.data = self.brain_file.get_data()
        self.images = self.data.shape[3]

    def load_stimuli(self, path, tr):
        self.stimuli = StimuliOnset(path, tr)

    def load_mask(self, mask):
        self.mask = mask

    def ready_for_calculation(self):
        return all([self.brain_file, self.stimuli, self.mask])

    def apply_mask(self, mask):
        """
        Apply the given mask to the brain and save the data for further
        calculations in the member masked_data.

        :param mask: Mask object which should be applied
        """
        self.masked_data = np.zeros((1, self.images))

        for i in range(self.images):
            visual_brain = mask.data * self.data[:, :, :, i]
            visual_brain_time = np.nonzero(visual_brain)
            self.masked_data[:, i] = np.mean(visual_brain[visual_brain_time])

    def separate_into_responses(self, visual_stimuli):
        number_of_stimuli = visual_stimuli.amount

        shortest_interval = min([j - i for i, j in zip(visual_stimuli.data[:-1, 0], visual_stimuli.data[1:, 0])])

        self.response = np.zeros((number_of_stimuli, shortest_interval))

        # Ignore the images after the last time stamp
        for i in range(number_of_stimuli - 1):
            start = visual_stimuli.data[i, 0]
            end = start + shortest_interval
            self.response[i, 0:(end - start)] = self.masked_data[:, (start - 1):(end - 1)]

    def normalize(self, percentage=False, global_=False):
        """
        Applies normalization on the response data depending on type and reference point.

        :param percentage: Whether percentual change from reference value should be shown.
        If false, data will be normalized by subtraction of the reference value.
        :param global_: Whether reference value should be the global mean.
        If false, reference value will be the start value of each sequence.
        """
        number_of_stimuli = self.response.shape[0]
        for i in range(number_of_stimuli):
            if global_:
                start = self.stimuli.data[i, 0]
                time_indexes = list(range(start, start + self.response.shape[1]))
                ref = np.mean(self.data[:, :, :, time_indexes], (0, 1, 2))     # Mean of spatial dimensions
            else:
                ref = np.ones(self.response.shape[1]) * self.response[i, 0]

            if percentage:
                if ref.all():
                    self.response[i, :] = (self.response[i, :] / ref - 1) * 100
            else:
                self.response[i, :] = self.response[i, :] - ref

    def calculate_mean(self):
        """ Calculate the mean response """
        response_mean = np.zeros((1, self.response.shape[1]))

        for i in range(self.response.shape[1]):
            rm1 = np.nonzero(self.response[:, i])
            if rm1[0].any():
                response_mean[:, i] = np.mean(self.response[rm1[0], i])

        return response_mean

    def calculate_std(self):
        """ Calculate the standard deviation of the response """
        response_std = np.zeros((1, self.response.shape[1]))

        for i in range(self.response.shape[1]):
            rm1 = np.nonzero(self.response[:, i])
            if rm1[0].any():
                response_std[:, i] = np.std(self.response[rm1[0], i], ddof=1)  # ddof=1 to work like MATLAB std()

        return response_std

    def calculate_sem(self):
        """ Calculate the standard error of the mean (SEM) of the response """
        response_sem = []

        for i in range(self.response.shape[1]):
            response_sem.append(sem(self.response[:, i]))
        return response_sem

    def plot_mean(self, fwhm=False):
        """ Plot the mean response.
        :param fwhm: A bool telling if we should plot fwhm
        """
        y = self.calculate_mean()[0]
        smoothing_factor = 20
        x = np.arange(y.size)

        self.plot_amplitude(x, y)
        if fwhm:
            r1, r2 = self.calculate_fwhm(x, y, smoothing_factor)
            plt.axvspan(r1, r2, facecolor='g', alpha=0.3)
        plt.plot(self.calculate_sem())
        plt.plot(y)
        plt.title('Average response (mean)')
        plt.axis([0, 45, -2, 19])
        plt.show()

    def plot_std(self):
        """ Plot the standard error of the response."""
        y = self.calculate_mean()[0]
        x = np.arange(y.size)

        plt.plot(self.calculate_sem())
        plt.errorbar(x, y, yerr=self.calculate_std()[0])
        plt.title('Average response (std)')
        plt.axis([0, 45, -20, 30])
        plt.show()

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

    def plot_amplitude(self, x, y):
        max_amp = self.calculate_amplitude(x, y, 0)
        plt.plot([x[0], x[-1]], [max_amp[1]] * 2, '--')
        plt.plot([max_amp[0]] * 2, [-100, 100], '--')

    def calculate(self):
        # Check if dimensions of 'Session' and 'Mask' match.
        if self.data.shape[0:3] != self.mask.data.shape:
            return 'Session image dimensions does not match Mask dimensions\n\nSession: ' \
                   + str(self.data.shape[0:3]) + '\nMask: ' + str(self.mask.data.shape)
        else:
            self.apply_mask(self.mask)
            self.separate_into_responses(self.stimuli)
            self.normalize(percentage=False, global_=True)
