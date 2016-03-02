class Brain:
    def __init__(self, path, session):
        self.path = path
        self.session = session
        self.id = self.session.load_nifti(path)
        self.masked_id = None
        self.data_id = None

    def apply_mask(self, mask):
        self.masked_id = self.session.apply_mask(self.id, mask.id)

    def normalize_to_mean(self, visual_stimuli):
        self.data_id = self.session.normalize_to_mean(self.masked_id, visual_stimuli.id)

    def calculate_mean(self):
        pass

    def calculate_std(self):
        pass

    def plot_mean(self):
        if self.data_id:
            self.session.plot_mean(self.data_id, nargout=0)

    def plot_std(self):
        if self.data_id:
            self.session.plot_std(self.data_id, nargout=0)
