from session import Session
from mask import Mask
from stimulionset import StimuliOnset
from plotWindow import CustomPlot


class Individual:

    def __init__(self, configuration=None):
        self.name = None
        self.sessions = []
        self.mask = None
        self.anatomic_image = None
        self.plot_settings = []

        if configuration:
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

    def plot(self):
        pass
