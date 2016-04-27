from mask import Mask
from session import Session
from stimulionset import StimuliOnset
import numpy as np
from data import Data


class Individual(Data):
    def __init__(self, configuration=None):
        super(Data, self).__init__()
        self.name = None
        self.sessions = []
        self.mask = None
        self.brain = None
        self.stimuli_onset = None
        self.anatomic_image = None
        self.plot_settings = []
        self.responses = {}

        if configuration:
            self.load_configuration(configuration)

    def load_configuration(self, configuration):
        if 'name' in configuration:
            self.name = configuration['name']

        if 'sessions' in configuration:
            for session_configuration in configuration['sessions']:
                self.sessions.append(Session(configuration=session_configuration))

        if 'brain' in configuration:
            self.brain = Session(configuration['brain']['path'])

        if 'mask' in configuration:
            self.mask = Mask(configuration['mask']['path'])

        if 'stimuli_onset' in configuration:
            path = configuration['stimuli_onset']['path']
            tr = configuration['stimuli_onset']['tr']

            self.stimuli_onset = StimuliOnset(path, tr)

        if 'name' in configuration:
            self.name = configuration['name']

    def get_configuration(self):
        configuration = {
            'name': self.name,
            'sessions': [session.get_configuration() for session in self.sessions]
        }

        return configuration

    def add_session(self, session):
        self.sessions.append(session)

    def remove_session(self, session):
        self.sessions.remove(session)

    def plot(self):
        pass

    def calculate_mean(self):
        """ Calculate the mean response """
        self.combine_session_responses()

        mean_responses = {}

        for stimuli_type, stimuli_data in self.responses.iteritems():
            response_mean = np.zeros((1, stimuli_data.shape[1]))

            for i in range(stimuli_data.shape[1]):
                rm1 = np.nonzero(stimuli_data[:, i])
                # TODO: Motivate this if-statement
                if len(rm1[0]) > 0:
                    response_mean[:, i] = np.mean(stimuli_data[rm1[0], i])

            mean_responses[stimuli_type] = response_mean
        return mean_responses

    def combine_session_responses(self):
        self.responses = {}
        for i in range(len(self.sessions)):
            # If the session doesn't have the files loaded, skip it.
            if not self.sessions[i].ready_for_calculation():
                continue
            session_response = self.sessions[i].calculate_mean()
            for intensity, data in session_response.iteritems():
                if intensity in self.responses:
                    self.responses[intensity] = np.concatenate((self.responses[intensity], data))
                else:
                    self.responses[intensity] = data

