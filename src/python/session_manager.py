import matlab.engine


class session_manager:
    def __init__(self):
        self.session = matlab.engine.connect_matlab()
        self.session.cd("src/matlab")

    def hello_world(self):
        self.session.hello_world(nargout=0)