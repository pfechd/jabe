function y = load_nifti(path)
    brain1 = load_nii(path,[],[],[],[],[],1);
    brain1 = brain1.img;
    brain1 = double(brain1);
    variable_name = matlab.lang.makeValidName(path);
    set_data(variable_name,brain1);
    y = variable_name;
end