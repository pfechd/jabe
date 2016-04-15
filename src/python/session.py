# -*- encoding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
from scipy.interpolate import UnivariateSpline
from scipy.stats import sem


class Session:
    """
    Class used for representing and doing calculations with brain data

    The brain data is initially read from a NIfTI-file (.nii) and the original
    data is stored in the member data
    """
    def __init__(self, path=None, configuration=None):
        if path:
            self.path = path
        elif configuration:
            self.path = configuration['path']
        else:
            raise NotImplementedError("This error message is not implemented")

        self.brain_file = nib.load(path)
        self.data = self.brain_file.get_data()
        self.images = self.data.shape[3]
        self.masked_data = None
        self.response = None

    def get_configuration(self):
        return {'path': self.path}

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

    def normalize_to_mean(self, visual_stimuli):
        """
        Normalize the function to mean with the given visual stimuli

        :param visual_stimuli: StimuliOnset object which should be used
        :return:
        """
        number_of_stimuli = visual_stimuli.amount
        self.response = np.zeros((number_of_stimuli - 1, self.images))
        max_nr_of_img = 0

        # Split up data into responses.
        for i in range(number_of_stimuli - 1):
            v1i = int(visual_stimuli.data[i, 0])
            v1i1 = int(visual_stimuli.data[i + 1, 0])

            number_of_images = v1i1 - v1i
            if number_of_images > max_nr_of_img:
                max_nr_of_img = number_of_images

            self.response[i, 0:number_of_images] = self.masked_data[:, (v1i-1):(v1i1-1)] - self.masked_data[:, v1i-1]

        self.response = self.response[:, 0:max_nr_of_img]


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
                response_std[:, i] = np.std(self.response[rm1[0], i], ddof=1) # ddof=1 to work like MATLAB std()

        return response_std

    def calculate_sem(self):
        """ Calculate the standard error of the mean (SEM) of the response """
        response_sem = []

        for i in range(self.response.shape[1]):
            response_sem.append(sem(self.response[:, i]))
        return response_sem

    def plot_mean(self, fwhm = False):
        """ Plot the mean response."""
        y = self.calculate_mean()[0]
        smoothing_factor = 20
        x = np.arange(y.size)

        self.plot_amplitude(x, y, smoothing_factor)
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
        """ Subtract baseline from a response """
        sub_value = response[0]

        for i in range(self.images):
            response[i] -= sub_value

        return response

    def get_voxel_size(self):
        """ Returns the size of one voxel in the image. """
        return self.brain_file._header.get_zooms()

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
        y[0] = y[-1] = 0     # Temporary code due to bugged y values

        assert 0 <= smoothing < len(y)
        half_maximum = np.max(y)/2
        spline = UnivariateSpline(x, y - half_maximum, s=smoothing)
        roots = spline.roots()
        try:
            assert len(roots) == 2   # Higher smoothing factor required
        except AssertionError:
            print "Smoothed function contains ", len(roots), " roots, 2 required"
            return 0, 1
        r1, r2 = roots
        # DEBUG
        #plt.plot(x, spline(x) + half_maximum)
        return r1, r2

    def calculate_amplitude(self, x, y, smoothing):

        spline = UnivariateSpline(x, y, s=smoothing) # Remove spline if smoothing is unnecessary
        max_amp = np.argmax(spline(x))
        return max_amp, spline(x)[max_amp]

    def plot_amplitude(self, x, y, smoothing):
        max_amp = self.calculate_amplitude(x, y, 0)
        plt.plot([x[0], x[-1]], [max_amp[1]] * 2, '--')
        plt.plot([max_amp[0]] * 2, [-100, 100], '--')

