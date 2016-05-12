import nibabel


class Brain:
    """
    Class used for representing and loading brain images.

    Currently only supports NIfTI1. The data is accessible via the member
    `data`.
    """
    def __init__(self, path):
        """
        :param path: The file path to the brain image/sequence.
        """
        self.path = path
        self.brain_file = nibabel.load(path)
        self.sequence = self.brain_file.get_data()

        if len(self.sequence.shape) < 4:
            self.images = 1
        else:
            self.images = self.sequence.shape[3]

    def get_voxel_size(self):
        """ Returns the size of one voxel in the image. """
        return self.brain_file._header.get_zooms()
