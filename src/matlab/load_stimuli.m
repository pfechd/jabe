function y = load_stimuli(path, tr)
    visual_stimuli = load(strcat(path,'.mat'))
    fieldNames = fieldnames(visual_stimuli);
    visual_stimuli=visual_stimuli.(fieldNames{:,1});
    v1 = [visual_stimuli(:,1)/tr];
    v1 = floor(v1);
    v1 = [v1 visual_stimuli(:,2)];
    set_data(path,v1);
    y = path;
end