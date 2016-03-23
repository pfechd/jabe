function y = calculate_mean(data)
    data = evalin('base', data);

    antalBilder = size(data,2);

    for b1 = 1:antalBilder
        rm1 = find(data(:,b1));
        response1_mean(b1) = mean(data(rm1,b1));
    end

    variable_name = matlab.lang.makeUniqueStrings('response_mean');
    set_data(variable_name, response1_mean);
    y = variable_name;
end