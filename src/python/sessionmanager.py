import matlab.engine


class SessionManager:
    """ Manager for setting up and handling a single connection to MATLAB."""
    def __init__(self):
        names = matlab.engine.find_matlab()
        if names:
            self.session = matlab.engine.connect_matlab(names[0])
        else:
            self.session = matlab.engine.connect_matlab()
            self.session.cd("src/matlab")

    def hello_world(self):
        self.session.hello_world(nargout=0)

    def set_data(self, name, data):
        self.session.set_data(name, data, nargout=0)

    def get_data(self, key):
        return self.session.get_data(key)
