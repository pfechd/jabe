class VisualStimuli:

    def __init__(self,path,tr,session):
        self.path = path
        self.session = session
        self.id = self.session.load_stimuli(path, tr)
