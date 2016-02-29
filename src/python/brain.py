from src.python.data import Data


class Brain:

    def __init__(self,path,session):
        self.path = path
        self.session = session
        self.id = self.session.load_nifti(path)
        self.masked_id = None

    def apply_mask(self, mask):
        self.masked_id = self.session.apply_mask(self.id, mask.id)

    def normalize_to_mean(self, visual_stimuli):
        data = self.session.normalize_to_mean(self.masked_id, visual_stimuli.id)
        return Data(data, self.session)

    def calculate_mean(self):
        pass

    def calculate_std(self):
        pass

