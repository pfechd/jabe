class Brain:

    def __init__(self,path,session):
        self.path = path
        self.session = session
        self.id = self.session.load_nifti(path)

    def apply_mask(self,mask):
        pass

    def normalize_to_mean(self):
        pass

    def calculate_mean(self):
        pass

    def calculate_std(self):
        pass

    def plot_mean(self):
        pass

    def plot_std(self):
        pass
