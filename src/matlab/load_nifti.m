function y = load_nifti(path)
    brain1 = load_nii(strcat(path,'.nii'),[],[],[],[],[],1)
    brain1 = brain1.img;
    brain1 = double(brain1);
    set_data(path,brain1);
    y = path;
end