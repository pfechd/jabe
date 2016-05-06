import nibabel as nib
import numpy as np
import os


class Mask:
    """ Representation of the mask data
    Class used for representing mask data

    The mask data is is read from a NIfTI-file (.nii). The data can be
    accessed through the member called data.
    """

    def __init__(self, path=None, shape=None, coordinate=None, width=None, brain_file=None):
        """ Load a mask from a path or create a mask from the specified data
        :param path: Path for the NIfTI file
        :param shape: The shape of the ROI, cube or sphere
        :param coordinate: Coordinates for the center point of the ROI
        :param width: The size of the ROI
        :param brain_file: The EPI-image
        """
        # If we do not get a width,then we load a path.
        # Otherwise we make a new mask with the specified data.
        if width == None:
            self.path = path
            mask_file = nib.load(path)
            self.data = mask_file.get_data()
        else:
            voxel_size = brain_file._header.get_zooms()
            size = brain_file.get_data().shape[0:3]

            # Create empty matrix of correct size
            self.data = np.zeros(size)


            # Set ones in a volume of a cube around the specified coordinate
            if shape == "cube":
                for z in range(coordinate[2] - width[2] / 2*voxel_size[2],
                               coordinate[2] + width[2] / 2*voxel_size[2] + 1):
                    for y in range(coordinate[1] - width[1] / 2*voxel_size[1],
                                   coordinate[1] + width[1] / 2*voxel_size[1] + 1):
                        for x in range(coordinate[0] - width[0] / 2*voxel_size[0],
                                       coordinate[0] + width[0] / 2*voxel_size[0] + 1):
                            self.data[z, y, x] = 1

            # Set ones in every coordinate within the distance radius_width around the coordinate, making it a sphere
            if shape == "sphere":
                for z in range(0, size[2]):
                    for y in range(0, size[1]):
                        for x in range(0, size[0]):
                            if (coordinate[2] - z) ** 2 + (coordinate[1] - y) ** 2 + (
                                        coordinate[0] - x) ** 2 <= width[0] ** 2:
                                self.data[z, y, x] = 1

            # Create a nifti file containing the data and save it to path
            mask_file = nib.Nifti1Image(self.data, np.eye(4,4))
            nib.save(mask_file, path)

    def get_configuration(self):
        return {'path': self.path}
