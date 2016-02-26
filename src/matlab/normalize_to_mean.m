function [variable_name] = normalize_to_mean(brain, visual_stimuli)
    b = evalin('base', brain);
    vs = evalin('base', visual_stimuli);

    antalStimuli = size(vs,1);
    
    for i = 1:antalStimuli-1
        numberOfImages = vs(i+1)-vs(i);
        out(i,1:(numberOfImages)) = b(vs(i):(vs(i+1)-1))- b(vs(i)); %cut out the time series for each response and put them at a row each in response1
    end
    
    variable_name = matlab.lang.makeUniqueStrings('data');
    assignin('base', variable_name, out);
end