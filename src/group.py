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

