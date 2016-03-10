function y = load_stimuli(path, tr)
    visual_stimuli = load(path);
    fieldNames = fieldnames(visual_stimuli);
    visual_stimuli=visual_stimuli.(fieldNames{:,1});
    v1 = [visual_stimuli(:,1)/tr];
    v1 = floor(v1);
    v1 = [v1 visual_stimuli(:,2)];
    variable_name = matlab.lang.makeValidName(path);
    set_data(variable_name,v1);
    y = variable_name;
end