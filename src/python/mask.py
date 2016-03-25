import nibabel as nib


class Mask:
    """ Representation of the mask data
    Class used for representing mask data

    The mask data is is read from a NifTI-file (.nii). The data can be
    accessed through the member called data.
    """
    def __init__(self, path):
        self.path = path
        mask_file = nib.load(path)
        self.data = mask_file.get_data()
