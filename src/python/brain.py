import matplotlib.pyplot as plt
import numpy as np
import scipy
import nibabel as nib


class Brain:
    def __init__(self, path):
        self.path = path
        brain_file = nib.load(path)
        self.data = brain_file.get_data()
        self.masked_data = None
        self.response = None

    def apply_mask(self, mask):
        images = self.data.shape[3]
        self.masked_data = np.zeros(images)

        for i in range(images):
            visual_brain = mask.data * self.data[:,:,:,i]
            visual_brain_time = np.nonzero(visual_brain) # Denna var knepig
            self.masked_data[i] = np.mean(visual_brain[visual_brain_time])


    def normalize_to_mean(self, visual_stimuli):
        number_of_stimuli = visual_stimuli.amount
        self.response = np.zeros((number_of_stimuli - 1, self.data.shape[3]))

        # Split up data into responses. (Tog mycket tid)
        for i in range(number_of_stimuli - 1):
            v1i = int(visual_stimuli.data[0, i])
            v1i1 = int(visual_stimuli.data[0, i + 1])
            number_of_images = v1i1 - v1i
            self.response[i, 0:number_of_images-1] = self.masked_data[v1i:v1i1-1] - self.masked_data[v1i]

    def calculate_mean(self):
        pass

    def calculate_std(self):
        pass

    def plot_mean(self):
        response_mean = np.zeros(self.data.shape[3])

        # Calculate average response
        for i in range(self.data.shape[3]):
            rm1 = np.nonzero(self.response[:, i])
            response_mean[i] = np.mean(self.response[:, i])

        # Plot average response
        plt.plot(response_mean)
        plt.title('Utraknat varde fran skript')
        plt.axis([0, 45, -2, 19])
        plt.show()

    def plot_std(self):
        response_std = np.zeros(self.data.shape[3])

        # Calculate average response
        for i in range(self.data.shape[3]):
            rm1 = np.nonzero(self.response[:, i])
            response_std[i] = np.std(self.response[:, i])

        # Plot average response
        plt.plot(response_std)
        plt.title('Utraknat varde fran skript')
        plt.axis([0, 45, -2, 19])
        plt.show()