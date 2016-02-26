function apply_mask(brain, mask)
    b = evalin('base', brain);
    m = evalin('base', mask);

    [~, ~, ~, images] = size(b);
    
    for i = 1:images
        b(:,:,:,i) = m.*b(:,:,:,i);
    end
    
    assignin('base', brain, b)
end