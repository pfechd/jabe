import nibabel as nib
import numpy as np

from session import Session


class Mask:
    """ Representation of the mask data
    Class used for representing mask data

    The mask data is is read from a NIfTI-file (.nii). The data can be
    accessed through the member called data.
    """

    def __init__(self, path=None, shape=None, coordinate=None, radius_width=None, brainfile=None):
        """ Load a mask from a path or create a mask from the specified data
        :param path: path for the NIfTI file
        :param shape: the shape of the ROI, cube or sphere
        :param coordinate: coordinates for the center point of the ROI
        :param radius_width: the size of the ROI
        :param size: the size of the mask
        :param voxel_size: the size in mm for each voxel
        """
        # if we get a path then we load that path, otherwise we make a new mask with the specified data
        if path is not None:
            self.path = path
            mask_file = nib.load(path)
            self.data = mask_file.get_data()
        else:
            voxel_size = Session.get_voxel_size()
            size = brainfile.get_data().shape[0:2]

            # create empty matrix of correct size
            self.data = np.zeros(size)

            # Convert coordinates and shape_size to mm
            radius_width /= voxel_size
            coordinate = (coordinate[0] / voxel_size, coordinate[1] / voxel_size, coordinate[2] / voxel_size)

            # set ones in a volume of a cube around the specified coordinate
            if shape == "cube":
                for z in range(coordinate[2] - radius_width / 2, coordinate[2] + radius_width / 2 + 1):
                    for y in range(coordinate[1] - radius_width / 2, coordinate[1] + radius_width / 2 + 1):
                        for x in range(coordinate[0] - radius_width / 2, coordinate[0] + radius_width / 2 + 1):
                            self.data[z, y, x] = 1

            # set ones in every coordinate within the distance shape_size around he coordinate, making it a sphere
            if shape == "sphere":
                for z in range(0, size[2]):
                    for y in range(0, size[1]):
                        for x in range(0, size[0]):
                            if (coordinate[2] - z) ** 2 + (coordinate[1] - y) ** 2 + (
                                        coordinate[0] - x) ** 2 <= radius_width ** 2:
                                self.data[z, y, x] = 1

    def get_configuration(self):
        return {'path': self.path}
