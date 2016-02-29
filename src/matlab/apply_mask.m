function y = apply_mask(brain, mask)
    b = evalin('base', brain);
    m = evalin('base', mask);

    [~, ~, ~, images] = size(b);
    
    for i = 1:images
        % b(:,:,:,i) = m.*b(:,:,:,i);
        vb = m.*b(:,:,:,i);
        vb_time = find(vb);
        in_vs(i) = mean(vb(vb_time));
    end

    variable_name = matlab.lang.makeUniqueStrings('in_visual_sphere');
    assignin('base', variable_name, in_vs);
    y = variable_name;
end