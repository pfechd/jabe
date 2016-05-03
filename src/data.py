import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.stats import sem
import nibabel as nib
from src.stimulionset import StimuliOnset


class Data(object):
    def __init__(self):
        self.name = None

        # The path to the file containing brain information
        self.path = None
        self.brain_file = None
        self.sequence = None
        self.images = None
        self.mask = None
        self.stimuli = None
        self.anatomy_path = None
        self.anatomy_file = None
        self.anatomic_image = None

        self.children = []
        # TODO: Remove this
        self.sessions = []

        # Normalization settings
        self.global_normalization = False
        self.percent_normalization = False

        # Result of calculations are kept here
        self.masked_data = None
        self.responses = {}

    def ready_for_calculation(self, stimuli=None, mask=None):
        if not stimuli:
            stimuli = self.stimuli
        if not mask:
            mask = self.mask

        children = self.children + self.sessions

        if children:
            return any([child.ready_for_calculation(stimuli, mask) for child in children])
        else:
            return all([self.brain_file, stimuli, mask])

    def separate_into_responses(self, stimuli, percentage, global_):
        number_of_stimuli = stimuli.amount

        shortest_interval = min([j - i for i, j in zip(stimuli.data[:-1, 0], stimuli.data[1:, 0])])

        self.responses = {}

        # Ignore the images after the last time stamp
        for i in range(number_of_stimuli - 1):
            start = stimuli.data[i, 0]
            end = start + shortest_interval
            response = self.masked_data[:, (start - 1):(end - 1)]
            response = self.normalize_sequence(start, end, response, percentage, global_)
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
        self.masked_data = np.zeros((1, self.images))

        for i in range(self.images):
            visual_brain = mask.data * self.sequence[:, :, :, i]
            visual_brain_time = np.nonzero(visual_brain)
            self.masked_data[:, i] = np.mean(visual_brain[visual_brain_time])

    def normalize_sequence(self, start, end, response, percentage, global_):
        """
        Applies normalization on the response data depending on type and reference point.

        :param start: the response sequence' start index in data.
        :param end: the response sequence' last index in data.
        :param response: the data sequence to be normalized
        :param percentage: Whether percentual change from reference value should be shown.
        If false, the response will be normalized by subtraction of the reference value.
        :param global_: Whether reference value should be the global mean.
        If false, reference value will be the start value of the response
        """
        if global_:
            time_indexes = list(range(start, end))
            ref = np.mean(self.sequence[:, :, :, time_indexes], (0, 1, 2))     # Mean of spatial dimensions
        else:
            ref = np.ones(end - start) * response[0][0]

        if percentage:
            if ref.all():
                return (response / ref - 1) * 100
        else:
            return response - ref

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

    def load_data(self, path):
        self.path = path
        self.brain_file = nib.load(path)
        self.sequence = self.brain_file.get_data()
        self.images = self.sequence.shape[3]

    def load_anatomy(self, path):
        self.anatomy_path = path
        self.anatomy_file = nib.load(path)
        self.anatomic_image = self.anatomy_file.get_data()

    def load_stimuli(self, path, tr):
        self.stimuli = StimuliOnset(path, tr)

    def load_mask(self, mask):
        self.mask = mask

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def get_tr(self):
        children = self.children + self.sessions
        # if we have a stimuli, use that tr. Otherwise check your children
        if self.stimuli:
            return self.stimuli.tr
        elif children:
            for child in children:
                #loop until we find a child that has a TR
                tr = child.get_tr()
                if tr:
                    return tr
        return None

    def settings_changed(self, percentage, global_, mask, stimuli):
        """
        Ask every child if the settings from their previous aggregation is
        different from the current settings
        """
        return any([child.settings_changed(percentage, global_,
                                           mask, stimuli)
                    for child in self.children + self.sessions])

    def aggregate(self, percentage=None, global_=None, mask=None, stimuli=None):
        """
        Aggregate response data from children with the given settings. This
        method caches data on all levels and only aggregates data when needed.

        :return: A dictionary stimuli-values as keys NxM matrices as values
                 where N is the number of stimuli and M is the length of the
                 shortest stimuli.
        """
        settings_changed = self.settings_changed(percentage, global_, mask, stimuli)

        if self.responses and not settings_changed:
            return self.responses
        else:
            return self._aggregate(percentage, global_, mask, stimuli)

    def calculate_mean(self):
        """
        Calculate the mean of every response grouped by stimuli type

        :return: A dictionary where the key is the stimuli type and the value
                 is the vector containing the mean value for the given time
                 frame.
        """
        responses = self.aggregate(self.percent_normalization, self.global_normalization)
        mean_responses = {}

        for stimuli_type, stimuli_data in responses.iteritems():
            response_mean = np.zeros(stimuli_data.shape[1])

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                # TODO: Motivate this if-statement
                if len(rm1[0]) > 0:
                    response_mean[i] = np.mean(stimuli_data[rm1[0], i])

            mean_responses[stimuli_type] = response_mean
        return mean_responses

    def calculate_sem(self):
        """ Calculate the standard error of the mean (SEM) of the response """
        responses = self.aggregate(self.percent_normalization, self.global_normalization)
        responses_sem = {}

        for stimuli_type, stimuli_data in responses.iteritems():
            response_sem = np.zeros(stimuli_data.shape[1])

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                if rm1[0].any():
                    response_sem[i] = sem(stimuli_data[rm1[0], i], ddof=1)

            responses_sem[stimuli_type] = response_sem

        return responses_sem
