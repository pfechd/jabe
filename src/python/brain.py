# -*- encoding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
from scipy.interpolate import UnivariateSpline


class Brain:
    """
    Class used for representing and doing calculations with brain data

    The brain data is initially read from a NIfTI-file (.nii) and the original
    data is stored in the member data
    """
    def __init__(self, path):
        self.path = path
        brain_file = nib.load(path)
        self.data = brain_file.get_data()
        self.images = self.data.shape[3]
        self.masked_data = None
        self.response = None

    def apply_mask(self, mask):
        """
        Apply the given mask to the brain and save the data for further
        calculations in the member masked_data.

        :param mask: Mask object which should be applied
        """
        self.masked_data = np.zeros(self.images)

        for i in range(self.images):
            visual_brain = mask.data * self.data[:, :, :, i]
            visual_brain_time = np.nonzero(visual_brain)
            self.masked_data[i] = np.mean(visual_brain[visual_brain_time])

    def normalize_to_mean(self, visual_stimuli):
        """
        Normalize the function to mean with the given visual stimuli

        :param visual_stimuli: VisualStimuli object which should be used
        :return:
        """
        number_of_stimuli = visual_stimuli.amount
        self.response = np.zeros((number_of_stimuli - 1, self.images))

        # Split up data into responses.
        for i in range(number_of_stimuli - 1):
            v1i = int(visual_stimuli.data[0, i])
            v1i1 = int(visual_stimuli.data[0, i + 1])
            number_of_images = v1i1 - v1i
            self.response[i, 0:number_of_images-1] = self.masked_data[v1i:v1i1-1] - self.masked_data[v1i]

    def calculate_mean(self):
        """ Calculate the mean response """
        response_mean = np.zeros(self.images)

        for i in range(self.images):
            rm1 = np.nonzero(self.response[:, i])
            response_mean[i] = np.mean(self.response[:, i])
        return response_mean

    def calculate_std(self):
        """ Calculate the standard error of the response """
        response_std = np.zeros(self.images)

        for i in range(self.images):
            rm1 = np.nonzero(self.response[:, i])
            response_std[i] = np.std(self.response[:, i])
        return response_std

    def plot_mean(self, fwhm = False):
        """ Plot the mean response."""
        y = self.calculate_mean()
        if fwhm:
            x = np.arange(y.size)
            smoothing_factor = 30
            r1, r2 = self.calculate_fwhm(x, y, smoothing_factor)
            plt.axvspan(r1, r2, facecolor='g', alpha=0.3)
        plt.plot(y)
        plt.title('Average response (mean)')
        plt.axis([0, 45, -2, 19])
        plt.show()

    def plot_std(self):
        """ Plot the standard error of the response."""
        y = self.calculate_mean()
        x = np.arange(y.size)

        plt.errorbar(x, y, yerr=self.calculate_std())
        plt.title('Average response (std)')
        plt.axis([0, 45, -20, 30])
        plt.show()

    def sub_from_baseline(self, response):
        """ Subtract baseline from a response """
        sub_value = response[0]

        for i in range(self.images):
            response[i] -= sub_value

        return response

    def calculate_fwhm(self, x, y, smoothing):
        """
        Returns two positions showing the full width half maximum(fwhm) of a given array y.

        Calculates two positions r1 and r2 on the x axis where y'[r1] and y'[r2]
        are equal to half of the maximum value of y where y' is a smoothed version of y.

        :param x: Time axis
        :param y: Value axis, for which fwhm is calculated
        :param smoothing: Smoothing factor for y. Must be less then the length of y and 0 or larger.
        0 gives no smoothing.
        :return: Two positions on the x axis.
        """

        assert 0 <= smoothing < len(y)
        half_maximum = np.max(y)/2
        spline = UnivariateSpline(x, y - half_maximum, s=smoothing)
        roots = spline.roots()
        assert len(roots) == 2   # Higher smoothing factor required
        r1, r2 = roots
        # DEBUG
        # plt.plot(x, spline(x) + half_maximum)
        return r1, r2
