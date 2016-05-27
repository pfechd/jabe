# Copyright (C) 2016 pfechd
#
# This file is part of JABE.
#
# JABE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# JABE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JABE.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.stats import sem
import nibabel as nib

from src.brain import Brain
from src.stimuli import Stimuli
from src.mask import Mask
import session


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
        self.tr = 1

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
        self.peaks = None

        if configuration:
            self.load_configuration(configuration)

    def ready_for_calculation(self, mask=None, stimuli=None):
        if not stimuli:
            stimuli = self.get_stimuli()
        if not mask:
            mask = self.get_mask()

        children = self.children + self.sessions

        if children:
            return any([child.ready_for_calculation(mask, stimuli) for child in children])
        else:
            return all([stimuli, mask])

    def get_fwhm(self, stimuli, factor):
        """
        Returns a dictionary with stimuli values as keys and x posisitions as values

        The x posisions are two positions on the x-axis that show where on the y axis
        the smoothed response with the stimuli value is at half its maximum value.
        The min value used is the value on the y axis when x equals 0.
        The max values is the position returend by self.get_peak.
        Raises Exception if no peak exists in the span or if not enough data points are
        avaliable for smoothing.

        :param stimuli: stimuli value for which fwhm is calculated.
        'All' means fwhm is calculated for all stimuli.
        :param factor: smoothing factor used for calculating fwhm.
        :return: Dictionary with stimuli values as keys and tuples with two floats as value
        """

        if not self.smoothed_responses:
            self.get_smooth(factor, splice=True)
        peaks = self.get_peaks(factor, smooth=True)

        def calculate_fwhm(stimuli):
            """
            Returns a tuple with positions on the x axis
            Assumes that stimuli exists in self.smooth_responses
            """
            top = peaks[stimuli][1]
            low = float(self.smoothed_responses[stimuli](0))
            half_max = (top - low)/2
            y = self.mean_responses[stimuli]
            spline = UnivariateSpline(self.x_axis, y - half_max - low, s=factor)
            roots = spline.roots()
            if np.any(roots):
                for i in range(1, len(roots)):
                    if roots[i] > peaks[stimuli][0]:
                        break
                roots = (roots[i - 1], roots[i])
            return roots

        if stimuli == "All":
            res = {}
            for stimuli in self.smoothed_responses.keys():
                res[stimuli] = calculate_fwhm(stimuli)
            return res
        else:
            return {stimuli: calculate_fwhm(stimuli)}

    def get_peaks(self, factor=0, smooth=False):
        """
        Return the coordinates the peak of every stimuli value in the group.

        :param factor: Smoothing factor used if peak of smoothed curve is used.
        :param smooth: Whether the peak from the smoothed curve or regular curve
        should be returned.
        If True, this function can raise an exception if a smoothed curve has no peak.
        """
        if not smooth:
            peaks = {}
            for stimuli_val, curve in self.mean_responses.iteritems():
                max = np.argmax(curve)
                pos = max * self.get_tr(), curve[max]
                peaks[stimuli_val] = pos
            return peaks

        if factor != self.smoothing_factor:
            self.get_smooth(factor, splice=False)

        if self.peaks:
            return self.peaks
        self.calculate_smooth_peaks()
        return self.peaks

    def calculate_smooth_peaks(self):
        """
        Calculate peaks of every curve in self.smoothed_responses and 
        stores them in self.peaks

        Raises an exception if a curve has no peak.
        """

        def calc_smooth_peak(curve):
            """
            Calculate the peak of given curve>
            Raises an exception if the curve has no peak.
            """
            roots = curve.derivative().roots()
            valid_roots = filter(
                    lambda x: x > self.x_axis[0] and x < self.x_axis[-1], roots)
            if valid_roots < 1:
                raise Exception
            top_root = valid_roots[np.argmax(curve(valid_roots))]
            return top_root, float(curve(top_root))

        self.peaks = {}

        for stimuli_val, curve in self.smoothed_responses.iteritems():
            try:
                self.peaks[stimuli_val] = calc_smooth_peak(curve)
            except Exception:
                raise Exception("Peak error", str(stimuli_val) + " has no valid peak")

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

    def load_stimuli(self, path):
        try:
            temp_stimuli = Stimuli(path)
        except:
            return "The file is not a proper stimuli file. It might be corrupted or in the wrong format"
        if isinstance(self, session.Session) and self.brain and temp_stimuli.data[-1, 0] > self.brain.images:
            return "The times in the stimuli file are too long compared to the length of the EPI sequence"
        else:
            self.stimuli = temp_stimuli
            self.stimuli.tr = self.tr
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
        elif isinstance(self, session.Session) and self.brain and self.brain.shape[0:3] != temp_mask.shape:
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
        if self.get_stimuli:
            return self.get_stimuli.tr
        elif children:
            for child in children:
                # loop until we find a child that has a TR
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

    def get_mean(self, percentage=None, global_=None, mask=None, stimuli=None):
        if percentage is None:
            percentage = self.get_setting('percent')
        if global_ is None:
            global_ = self.get_setting('global')
        if mask is None:
            mask = self.get_mask()
        if stimuli is None:
            stimuli = self.get_stimuli()

        settings_changed = self.settings_changed(percentage, global_,
                                                 mask, stimuli)
        if settings_changed or not self.mean_responses:
            self.mean_responses = self.calculate_mean(percentage, global_, mask, stimuli)
        return self.mean_responses

    def calculate_mean(self, percentage, global_, mask, stimuli):
        """
        Calculate the mean of every response grouped by stimuli type

        :return: A dictionary where the key is the stimuli type and the value
                 is the vector containing the mean value for the given time
                 frame.
        """
        responses = self.aggregate(percentage, global_, mask, stimuli)
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

    def get_smooth(self, factor, splice=False):
        """
        Returnes the smoothed responses in the group.

        Raises an Exception if a curve has too few data points for smoothing.
        :param factor: smoothing factor used
        :param splice: Whether splice data shoud be returned or samples from
        the spiced data on the x values in self.x_axis
        :return: A dictionary with stimuli values as keys and curves as values.
        If splice = False curves are of type numpy.array. If splice = True
        curves are of type scipy.interpolate.UnivariateSpline
        """
        if not self.smoothed_responses:
            self.smoothing_factor = factor
            self.peaks = None
            self.calculate_smooth()
        if factor != self.smoothing_factor:
            self.smoothing_factor = factor
            self.peaks = None
            for stim, curve in self.smoothed_responses.iteritems():
                curve.set_smoothing_factor(s=factor)
        if splice:
            return self.smoothed_responses
        smoothed_curves = {}
        for key in self.smoothed_responses:
            smoothed_curves[key] = self.smoothed_responses[key](self.x_axis)
        return smoothed_curves

    def calculate_smooth(self):
        """
        Calculates smoothed curves for each stimuli value in the group and 
        stores them in self.smoothed_responses.
        Raises Exception if a curve has too few data points for smoothing.
        """
        responses = self.get_mean()
        self.smoothed_responses = {}
        for key in responses.keys():
            response = responses[key]
            try:
                self.smoothed_responses[key] = UnivariateSpline(
                        self.x_axis, response, k=4, s=self.smoothing_factor)
            except:
                raise Exception("Smoothing error", 
                        "Not enough data points for smoothing")

    def get_x_axis(self):
        return self.x_axis * self.get_tr()

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
        responses = self.aggregate(percentage, global_, self.get_mask(), self.get_stimuli())
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
        configuration = {
            'name': self.name,
            'description': self.description,
            'plot_settings': self.plot_settings,
            'sessions': [session.get_configuration() for session in self.sessions],
            'tr': self.tr,
            'groups': [group.get_configuration() for group in self.children],
        }
        if self.anatomy:
            configuration['anatomy_path'] = self.anatomy.path

        if self.mask:
            configuration['mask'] = self.mask.get_configuration()

        if self.stimuli:
            configuration['stimuli'] = self.stimuli.get_configuration()

        return configuration

    def load_configuration(self, configuration):
        if 'name' in configuration:
            self.name = configuration['name']
        if 'anatomy_path' in configuration:
            self.load_anatomy(configuration['anatomy_path'])
        if 'mask' in configuration:
            self.load_mask(configuration['mask']['path'])
        if 'stimuli' in configuration:
            self.load_stimuli(configuration['stimuli']['path'], configuration['stimuli']['tr'])
        if 'description' in configuration:
            self.description = configuration['description']
        if 'plot_settings' in configuration:
            self.plot_settings = configuration['plot_settings']
        if 'tr' in configuration:
            self.tr = configuration['tr']

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
        self.peaks = None

        if not mask:
            mask = self.get_mask()
        if stimuli:
            tr = stimuli.tr
        else:
            stimuli = self.get_stimuli()
            tr = self.get_tr()

        for child in self.children + self.sessions:
            # If the child doesn't have the files loaded, skip it.
            if not child.ready_for_calculation(mask, stimuli):
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

        self.x_axis = np.array(list(range(min_width)))

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

    def get_mask(self):
        if isinstance(self, session.Session) or self.get_setting('use_mask'):
            return self.mask
        else:
            return None

    def get_stimuli(self):
        if isinstance(self, session.Session) or self.get_setting('use_stimuli'):
            return self.stimuli
        else:
            return None
