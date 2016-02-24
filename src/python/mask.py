class Mask:

    def __init__(self,path,session):
        self.path = path
        self.session = session
        self.id = self.session.load_nifti(path)