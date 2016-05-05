import nibabel as nib
import numpy as np
import os


class Mask:
    """ Representation of the mask data
    Class used for representing mask data

    The mask data is is read from a NIfTI-file (.nii). The data can be
    accessed through the member called data.
    """

    def __init__(self, path=None, shape=None, coordinate=None, radius_width=None, brain_file=None):
        """ Load a mask from a path or create a mask from the specified data
        :param path: path for the NIfTI file
        :param shape: the shape of the ROI, cube or sphere
        :param coordinate: coordinates for the center point of the ROI
        :param radius_width: the size of the ROI
        :param brain_file: the brain file
        """
        # if we get a path then we load that path, otherwise we make a new mask with the specified data
        if radius_width == None:
            self.path = path
            mask_file = nib.load(path)
            self.data = mask_file.get_data()
        else:
            voxel_size = brain_file._header.get_zooms()
            size = brain_file.get_data().shape[0:3]

            # create empty matrix of correct size
            self.data = np.zeros(size)

            # Convert coordinates and shape_size to mm
            coordinate = (coordinate[0] / voxel_size[0], coordinate[1] / voxel_size[1], coordinate[2] / voxel_size[2])

            # set ones in a volume of a cube around the specified coordinate
            if shape == "cube":
                for z in range(coordinate[2] - radius_width[2] / 2*voxel_size[2],
                               coordinate[2] + radius_width[2] / 2*voxel_size[2] + 1):
                    for y in range(coordinate[1] - radius_width[1] / 2*voxel_size[1],
                                   coordinate[1] + radius_width[1] / 2*voxel_size[1] + 1):
                        for x in range(coordinate[0] - radius_width[0] / 2*voxel_size[0],
                                       coordinate[0] + radius_width[0] / 2*voxel_size[0] + 1):
                            self.data[z, y, x] = 1

            # set ones in every coordinate within the distance radius_width around the coordinate, making it a sphere
            if shape == "sphere":
                for z in range(0, size[2]):
                    for y in range(0, size[1]):
                        for x in range(0, size[0]):
                            if (coordinate[2] - z) ** 2 + (coordinate[1] - y) ** 2 + (
                                        coordinate[0] - x) ** 2 <= radius_width[0] ** 2:
                                self.data[z, y, x] = 1

            # Create a nifti file containing the data and save it to path
            mask_file = nib.Nifti1Image(self.data, np.eye(4,4))
            nib.save(mask_file, path)

    def get_configuration(self):
        return {'path': self.path}
