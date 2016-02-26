class Brain:

    def __init__(self,path,session):
        self.path = path
        self.session = session
        self.id = self.session.load_nifti(path)

    def apply_mask(self, mask):
        self.session.apply_mask(self.id, mask.id, nargout=0)

    def normalize_to_mean(self, visual_stimuli):
        self.session.normalize_to_mean(self.id, visual_stimuli.id, nargout=0)

    def calculate_mean(self):
        pass

    def calculate_std(self):
        pass

    def plot_mean(self):
        self.session.plot_mean(self.id, nargout=0)

    def plot_std(self):
        self.session.plot_std(self.id, nargout=0)

