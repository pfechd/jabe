import nibabel as nib
import numpy as np

class Mask:
    """ Representation of the mask data
    Class used for representing mask data

    The mask data is is read from a NifTI-file (.nii). The data can be
    accessed through the member called data.
    """
    def __init__(self, path = None, coordinates = None, size = None, shape = None, shape_size = None):
        if path is not None:
            self.path = path
            mask_file = nib.load(path)
            self.data = mask_file.get_data()
        else:
            # create empty matrix of correct size
            self.data = np.zeros(size)

                
            # set ones on the correct coordinate and with a specified shape
            if shape == "cube":
                for z in range(coordinates[2] - shape_size/2, coordinates[2] + shape_size/2):
                    for y in range(coordinates[1] - shape_size/2, coordinates[1] + shape_size/2):
                        for x in range(coordinates[0] - shape_size/2, coordinates[0] + shape_size/2):
                            self.data[z,y,x] = 1

