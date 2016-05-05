import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.stats import sem
import nibabel as nib

from src.brain import Brain
from src.stimulionset import StimuliOnset


class Group(object):
    """
    Class containing methods for analysing a group of groups and
    groups of sessions recursively.
    """
    def __init__(self, configuration=None):
        self.name = ""
        self.description = ""
        self.plot_settings = {}

        self.mask = None
        self.stimuli = None
        self.anatomy = None

        self.children = []
        # TODO: Remove this
        self.sessions = []

        # Result of calculations are kept here
        self.responses = {}

        if configuration:
            self.load_configuration(configuration)

    def ready_for_calculation(self, stimuli=None, mask=None):
        if not stimuli:
            stimuli = self.stimuli
        if not mask:
            mask = self.mask

        children = self.children + self.sessions

        if children:
            return any([child.ready_for_calculation(stimuli, mask) for child in children])
        else:
            return all([stimuli, mask])

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

    def load_anatomy(self, path):
        self.anatomy = Brain(path)

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
        responses = self.aggregate(self.plot_settings['percent'], self.plot_settings['global'])
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
        responses = self.aggregate(self.plot_settings['percent'], self.plot_settings['global'])
        responses_sem = {}

        for stimuli_type, stimuli_data in responses.iteritems():
            response_sem = np.zeros(stimuli_data.shape[1])

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                if rm1[0].any():
                    response_sem[i] = sem(stimuli_data[rm1[0], i], ddof=1)

            responses_sem[stimuli_type] = response_sem

        return responses_sem

    def get_configuration(self):
        return {
            'name': self.name,
            'description': self.description,
            'plot_settings': self.plot_settings,
            'individuals': [individual.get_configuration() for individual in self.children],
            'sessions': [session.get_configuration() for session in self.sessions]
        }

    def load_configuration(self, configuration):
        if 'name' in configuration:
            self.name = configuration['name']
        if 'description' in configuration:
            self.description = configuration['description']
        if 'plot_settings' in configuration:
            self.plot_settings = configuration['plot_settings']

    def add_session(self, session):
        self.sessions.append(session)

    def remove_session(self, session):
        self.sessions.remove(session)

    def _aggregate(self, percentage, global_, mask, stimuli):
        self.responses = {}
        min_width = float('inf')

        for child in self.children + self.sessions:
            # If the child doesn't have the files loaded, skip it.
            if not child.ready_for_calculation():
                continue
            child_response = child.aggregate(percentage, global_, mask, stimuli)

            for intensity, data in child_response.iteritems():
                min_width = min(min_width, data.shape[1])

                if intensity in self.responses:
                    responses = self.responses[intensity][:, 0:min_width]
                    data = data[:, 0:min_width]
                    self.responses[intensity] = np.concatenate((responses, data))
                else:
                    self.responses[intensity] = data

        # Set all data to match the length of the least wide response
        for intensity, data in self.responses.iteritems():
            self.responses[intensity] = data[:, 0:min_width]

        return self.responses

    def get_setting(self, setting):
        """ Return the specified plot setting. To simplify the code, it is assumed as False if it does not exist """
        if setting in self.plot_settings:
            return self.plot_settings[setting]
        else:
            return False
