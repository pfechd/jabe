import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib


class Brain:
    """
    Class used for representing and doing calculations with brain data

    The brain data is initially read from a NIfTI-file (.nii) and the original
    data is stored in the member data
    """
    def __init__(self, path):
        self.path = path
        brain_file = nib.load(path)
        self.data = brain_file.get_data()
        self.images = self.data.shape[3]
        self.masked_data = None
        self.response = None

    def apply_mask(self, mask):
        """
        Apply the given mask to the brain and save the data for further
        calculations in the member masked_data.

        :param mask: Mask object which should be applied
        """
        self.masked_data = np.zeros(self.images)

        for i in range(self.images):
            visual_brain = mask.data * self.data[:, :, :, i]
            visual_brain_time = np.nonzero(visual_brain)
            self.masked_data[i] = np.mean(visual_brain[visual_brain_time])

    def normalize_to_mean(self, visual_stimuli):
        """
        Normalize the function to mean with the given visual stimuli

        :param visual_stimuli: VisualStimuli object which should be used
        :return:
        """
        number_of_stimuli = visual_stimuli.amount
        self.response = np.zeros((number_of_stimuli - 1, self.images))

        # Split up data into responses.
        for i in range(number_of_stimuli - 1):
            v1i = int(visual_stimuli.data[0, i])
            v1i1 = int(visual_stimuli.data[0, i + 1])
            number_of_images = v1i1 - v1i
            self.response[i, 0:number_of_images-1] = self.masked_data[v1i:v1i1-1] - self.masked_data[v1i]

    def calculate_mean(self):
        # TODO: Extract the calculation part of plot_mean function
        pass

    def calculate_std(self):
        # TODO: Extract the calculation part of plot_std function
        pass

    def plot_mean(self):
        """ Plot the mean response."""
        response_mean = np.zeros(self.images)

        # Calculate average response
        for i in range(self.data.shape[3]):
            rm1 = np.nonzero(self.response[:, i])
            response_mean[i] = np.mean(self.response[:, i])

        # Plot average response
        plt.plot(response_mean)
        plt.title('Average response (mean)')
        plt.axis([0, 45, -2, 19])
        plt.show()

    def plot_std(self):
        """ Plot the standard error of the response."""
        response_std = np.zeros(self.data.shape[3])

        # Calculate the standard error of the response
        for i in range(self.data.shape[3]):
            rm1 = np.nonzero(self.response[:, i])
            response_std[i] = np.std(self.response[:, i])

        # Plot the standard error of the response
        plt.plot(response_std)
        plt.title('Average response (std)')
        plt.axis([0, 45, -2, 19])
        plt.show()
