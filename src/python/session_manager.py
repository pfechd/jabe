import matlab.engine


class session_manager:
    def __init__(self):
        self.session = matlab.engine.connect_matlab()
        self.session.cd("src/matlab")

    def hello_world(self):
        self.session.hello_world(nargout=0)

    def create_data_list(self):
        self.session.create_data_list(nargout=0)

    def add_data(self,name,data):
        self.session.add_data(name,str(data),nargout=0)

    def get_data(self,key):
        return self.session.get_data(key)