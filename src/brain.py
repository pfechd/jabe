import nibabel


class Brain:
    def __init__(self, path):
        """


        :param path: The file path to the brain.
        """
        self.path = path
        self.brain_file = nibabel.load(path)
        self.sequence = self.brain_file.get_data()
        self.images = self.sequence.shape[3]
