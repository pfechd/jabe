from data import Data
import numpy as np
from session import Session


class Group(Data):
    def __init__(self, name=None, configuration=None):
        super(Group, self).__init__()

        self.sessions = []

        if configuration:
            self.load_configuration(configuration)
        elif name:
            self.name = name

    def get_configuration(self):
        return {
            'name': self.name,
            'individuals': [individual.get_configuration() for individual in self.children],
            'sessions': [session.get_configuration() for session in self.sessions]
        }

    def load_configuration(self, configuration):
        if 'name' in configuration:
            self.name = configuration['name']

    def calculate_mean(self):
        """
        Calculate the mean of every response grouped by stimuli type

        :return: A dictionary where the key is the stimuli type and the value
                 is the vector containing the mean value for the given time
                 frame.
        """
        self.combine_children_responses()

        mean_responses = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_mean = np.zeros(stimuli_data.shape[1])

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                # TODO: Motivate this if-statement
                if len(rm1[0]) > 0:
                    response_mean[i] = np.mean(stimuli_data[rm1[0], i])

            mean_responses[stimuli_type] = response_mean
        return mean_responses

    def add_session(self, session):
        self.sessions.append(session)

    def remove_session(self, session):
        self.sessions.remove(session)

    def combine_children_responses(self):
        self.responses = {}
        children = self.children + self.sessions

        for child in children:
            # If the child doesn't have the files loaded, skip it.
            if not child.ready_for_calculation():
                continue
            session_response = child.calculate_mean()
            for intensity, data in session_response.iteritems():
                if intensity in self.responses:
                    self.responses[intensity] = np.concatenate((self.responses[intensity], data.reshape(1, data.shape[0])))
                else:
                    self.responses[intensity] = data.reshape(1, data.shape[0])


