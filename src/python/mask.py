import nibabel as nib


class Mask:
    def __init__(self, path):
        self.path = path
        mask_file = nib.load(path)
        self.data = mask_file.get_data()
