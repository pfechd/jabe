import nibabel


class Brain:
    def __init__(self, path):
        """


        :param path: The file path to the brain.
        """
        self.path = path
        self.brain_file = nibabel.load(path)
        self.sequence = self.brain_file.get_data()

        if len(self.sequence.shape) < 4:
            self.images = 1
        else:
            self.images = self.sequence.shape[3]
