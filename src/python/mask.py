import nibabel as nib
import numpy as np

class Mask:
    """ Representation of the mask data
    Class used for representing mask data

    The mask data is is read from a NifTI-file (.nii). The data can be
    accessed through the member called data.
    """
    def __init__(self, path = None, coordinates = None, size = None, shape = None, shape_size = None):
        # if we get a path then we load that path, otherwise we make a new mask with the specified data
        if path is not None:
            self.path = path
            mask_file = nib.load(path)
            self.data = mask_file.get_data()
        else:
            # create empty matrix of correct size
            self.data = np.zeros(size)

                
            # set ones in a volume of a cube around the specified coordinate
            if shape == "cube":
                for z in range(coordinates[2] - shape_size/2, coordinates[2] + shape_size/2+1):
                    for y in range(coordinates[1] - shape_size/2, coordinates[1] + shape_size/2+1):
                        for x in range(coordinates[0] - shape_size/2, coordinates[0] + shape_size/2+1):
                            self.data[z,y,x] = 1

            # set ones in every coordinate within the distance shape_siez around he coordinate, making it a sphere
            if shape == "sphere":
                for z in range(0,size[2]):
                    for y in range(0,size[1]):
                        for x in range(0,size[0]):
                            if (coordinates[2]-z)**2 + (coordinates[1] - y)**2 + (coordinates[0] - x)**2 <= shape_size**2:
                                self.data[z,y,x] = 1

