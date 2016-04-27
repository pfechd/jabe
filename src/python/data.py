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

    def ready_for_calculation(self):
        return all([self.brain_file, self.stimuli, self.mask])

    def prepare_for_calculation(self, mask=None, stimuli=None):
        if not mask:
            mask = self.mask
        if not stimuli:
            stimuli = self.stimuli

        if self.brain_file:
            # Calculate the responses with the masks and stimuli
            self.apply_mask(mask)
            self.separate_into_responses(mask, stimuli)
            self.normalize_local()
        elif self.children:
            # Load children
            for child in self.children:
                if not child.ready_for_calculation():
                    continue
                child.prepare_for_calculation(mask, stimuli)

    def separate_into_responses(self, mask, stimuli):
        number_of_stimuli = stimuli.amount

        shortest_interval = min([j - i for i, j in zip(stimuli.data[:-1, 0], stimuli.data[1:, 0])])

        # TODO: Apply the mask to the sequence
        self.responses = {}

        # Ignore the images after the last time stamp
        for i in range(number_of_stimuli - 1):
            start = stimuli.data[i, 0]
            end = start + shortest_interval
            response = self.masked_data[:, (start - 1):(end - 1)]
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

    def normalize_local(self):
        """
        Subtract every value of the response with the local baseline.

        :return:
        """
        for stimuli_type, values in self.responses.iteritems():
            number_of_stimuli = values.shape[0]
            for i in range(number_of_stimuli):
                self.responses[stimuli_type][i, :] = self.responses[stimuli_type][i, :] - self.responses[stimuli_type][i, 0]

