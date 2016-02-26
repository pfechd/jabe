from src.python.data import Data


class Brain:

    def __init__(self,path,session):
        self.path = path
        self.session = session
        self.id = self.session.load_nifti(path)

    def apply_mask(self, mask):
        self.session.apply_mask(self.id, mask.id, nargout=0)

    def normalize_to_mean(self, visual_stimuli):
        data = self.session.normalize_to_mean(self.id, visual_stimuli.id)
        return Data(data, self.session)

    def calculate_mean(self):
        pass

    def calculate_std(self):
        pass

