import numpy as np


class Data(object):
    def __init__(self):
        self.name = None

        self.brain_file = None
        self.sequence = None
        self.mask = None
        self.stimuli = None
        self.anatomic_image = None

        self.children = []

        self.plot_settings = {}

        # Result of calculations are kept here
        self.masked_data = None
        self.responses = {}

    def ready_for_calculation(self, stimuli=None, mask=None):
        if not stimuli:
            stimuli = self.stimuli
        if not mask:
            mask = self.mask

        if self.children:
            return any([child.ready_for_calculation(stimuli, mask) for child in self.children])
        else:
            return all([self.brain_file, stimuli, mask])

    def prepare_for_calculation(self, percentage, global_, mask=None, stimuli=None):
        if not mask:
            mask = self.mask
        if not stimuli:
            stimuli = self.stimuli

        if self.brain_file:
            # Calculate the responses with the masks and stimuli
            self.apply_mask(mask)
            self.separate_into_responses(stimuli, percentage, mask)
        elif self.children:
            # Load children
            for child in self.children:
                if not child.ready_for_calculation():
                    continue
                child.prepare_for_calculation(percentage, global_, mask, stimuli)

    def separate_into_responses(self, stimuli, percentage, global_):
        number_of_stimuli = stimuli.amount

        shortest_interval = min([j - i for i, j in zip(stimuli.data[:-1, 0], stimuli.data[1:, 0])])

        # TODO: Apply the mask to the sequence
        self.responses = {}

        # Ignore the images after the last time stamp
        for i in range(number_of_stimuli - 1):
            start = stimuli.data[i, 0]
            end = start + shortest_interval
            response = self.masked_data[:, (start - 1):(end - 1)]
            response = self.normalize_sequence(start, end, response, percentage, global_)
            intensity = stimuli.data[i, 1]
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
