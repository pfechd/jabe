class Data:
    def __init__(self, data, session):
        self.id = data
        self.session = session

    def plot_mean(self):
        self.session.plot_mean(self.id, nargout=0)

    def plot_std(self):
        self.session.plot_std(self.id, nargout=0)
