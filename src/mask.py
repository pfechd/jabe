import nibabel as nib
import numpy as np


class Mask:
    """ Representation of the mask data
    Class used for representing mask data

    The mask data is is read from a NIfTI-file (.nii). The data can be
    accessed through the member called data.
    """

    def __init__(self, path=None, coordinates=None, size=None, voxel_size=None, shape=None, shape_size=None):
        """ Load a mask from a path or create a mask from the specified data
        :param path: path for the NIfTI file
        :param coordinates: coordinates for the center point of the ROI
        :param size: the size of the mask
        :param voxel_size: the size in mm for each voxel
        :param shape: the shape of the ROI, cube or sphere
        :param shape_size: the size of the ROI
        """
        # if we get a path then we load that path, otherwise we make a new mask with the specified data
        if path is not None:
            self.path = path
            mask_file = nib.load(path)
            self.data = mask_file.get_data()
        else:
            # create empty matrix of correct size
            self.data = np.zeros(size)

            # Convert coordinates and shape_size to mm
            shape_size /= voxel_size
            coordinates = (coordinates[0] / voxel_size, coordinates[1] / voxel_size, coordinates[2] / voxel_size)

            # set ones in a volume of a cube around the specified coordinate
            if shape == "cube":
                for z in range(coordinates[2] - shape_size / 2, coordinates[2] + shape_size / 2 + 1):
                    for y in range(coordinates[1] - shape_size / 2, coordinates[1] + shape_size / 2 + 1):
                        for x in range(coordinates[0] - shape_size / 2, coordinates[0] + shape_size / 2 + 1):
                            self.data[z, y, x] = 1

            # set ones in every coordinate within the distance shape_size around he coordinate, making it a sphere
            if shape == "sphere":
                for z in range(0, size[2]):
                    for y in range(0, size[1]):
                        for x in range(0, size[0]):
                            if (coordinates[2] - z) ** 2 + (coordinates[1] - y) ** 2 + (
                                        coordinates[0] - x) ** 2 <= shape_size ** 2:
                                self.data[z, y, x] = 1

    def get_configuration(self):
        return {'path': self.path}

    def get_index_of_roi(self):
        most_ones = np.array([[0,0,0,1]])
        ones_amount = 0
        for i in range(self.data.shape[0]):
            ones = np.count_nonzero(self.data[i,:,:])
            if ones > ones_amount:
                ones_amount = ones
                most_ones[0][0] = i


        ones_amount = 0
        for i in range(self.data.shape[1]):
            ones = np.count_nonzero(self.data[:,i,:])
            if ones > ones_amount:
                ones_amount = ones
                most_ones[0][1] = i


        ones_amount = 0
        for i in range(self.data.shape[2]):
            ones = np.count_nonzero(self.data[:,:,i])
            if ones > ones_amount:
                ones_amount = ones
                most_ones[0][2] = i

        return most_ones





