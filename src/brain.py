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

    def get_voxel_size(self):
        """ Returns the size of one voxel in the image. """
        return self.brain_file._header.get_zooms()

    @property
    def shape(self):
        return self.brain_file.shape

    @property
    def sequence(self):
        return self.brain_file.get_data()

    @property
    def images(self):
        if self.brain_file.shape < 4:
            return 1
        else:
            return self.brain_file.shape[3]
