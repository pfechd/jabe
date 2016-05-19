import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.stats import sem
import nibabel as nib

from src.brain import Brain
from src.stimuli import Stimuli
from src.mask import Mask


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
        self.mean_responses = {}
        self.sem_responses = {}
        self.smoothed_responses = None
        self.smoothing_factor = None
        self.x_axis = None

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
        try:
            temp_anatomy = Brain(path)
        except IOError:
            return path + " does not exist"
        except:
            return path + " could not be opened. It might be corrupted"
        if len(temp_anatomy.shape) != 3:
            return "The data has " + str(len(temp_anatomy.shape)) + " dimensions instead of 3"
        else:
            self.anatomy = temp_anatomy
            return None

    def load_stimuli(self, path, tr):
        try:
            temp_stimuli = Stimuli(path, tr)
        except:
            return "The file is not a proper stimuli file. It might be corrupted or in the wrong format"
        if self.brain and temp_stimuli.data[-1, 0] > self.brain.images:
            return "The times in the stimuli file are too long compared to the length of the EPI sequence"
        else:
            self.stimuli = temp_stimuli
            return None

    def load_mask(self, path):
        try:
            temp_mask = Mask(path)
        except IOError:
            return path + " does not exist"
        except:
            return path + " could not be opened. It might be corrupted"
        if len(temp_mask.shape) != 3:
            return "The data has " + str(len(temp_mask.shape)) + " dimensions instead of 3"
        elif self.brain and self.brain.shape[0:3] != temp_mask.shape:
            return "The mask is not the same size as the EPI sequence"
        else:
            self.mask = temp_mask
            return None

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

    def get_mean(self, percentage=None, global_=None):
        if percentage is None:
            percentage = self.get_setting('percent')
        if global_ is None:
            global_ = self.get_setting('global')

        settings_changed = self.settings_changed(percentage, global_,
                                                 self.mask, self.stimuli)
        if settings_changed or not self.mean_responses:
            self.mean_responses = self.calculate_mean(percentage, global_)
        return self.mean_responses

    def calculate_mean(self, percentage, global_):
        """
        Calculate the mean of every response grouped by stimuli type

        :return: A dictionary where the key is the stimuli type and the value
                 is the vector containing the mean value for the given time
                 frame.
        """

        responses = self.aggregate(percentage, global_)
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

    def get_smooth(self, factor):
        if factor != self.smoothing_factor or not self.smoothed_responses:
            self.smoothing_factor = factor
            self.calculate_smooth()
        smoothed_curves = {}
        for key in self.smoothed_responses:
            smoothed_curves[key] = self.smoothed_responses[key](self.x_axis)
        return smoothed_curves

    def calculate_smooth(self):
        """
        Assumes all vectors returned from self.get_mean() are of equal length
        """
        responses = self.get_mean()
        self.smoothed_responses = {}
        for key in responses.keys():
            response = responses[key]
            self.smoothed_responses[key] = UnivariateSpline(self.x_axis, response, s=self.smoothing_factor)

    def get_x_axis(self):
        return self.x_axis

    def get_sem(self, percentage=None, global_=None):
        if percentage is None:
            percentage = self.get_setting('percent')
        if global_ is None:
            global_ = self.get_setting('global')

        settings_changed = self.settings_changed(percentage, global_,
                                                 self.mask, self.stimuli)
        if settings_changed or not self.sem_responses:
            self.sem_responses = self.calculate_sem(percentage, global_)
        return self.sem_responses

    def calculate_sem(self, percentage, global_):
        """ Calculate the standard error of the mean (SEM) of the response """

        responses = self.aggregate(percentage, global_)
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

        # Invalidate cached mean and sem
        self.sem_responses = None
        self.mean_responses = None
        self.smoothed_responses = None

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

        self.x_axis = np.array(list(range(min_width))) * self.get_tr()

        # Set all data to match the length of the least wide response
        for intensity, data in self.responses.iteritems():
            self.responses[intensity] = data[:, 0:min_width]

        return self.responses

    def get_setting(self, setting):
        """ 
        Return the specified plot setting. 
        To simplify the code, it is assumed as False if it does not exist 
        """
        if setting in self.plot_settings:
            return self.plot_settings[setting]
        else:
            return False
