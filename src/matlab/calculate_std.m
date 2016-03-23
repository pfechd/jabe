function y = calculate_std(data)
    data = evalin('base', data);

    antalBilder = size(data,2);

    for b1 = 1:antalBilder
        rm1 = find(data(:,b1));
        response1_std(b1) = std(data(rm1,b1));
    end

    variable_name = matlab.lang.makeUniqueStrings('response_std');
    set_data(variable_name, response1_std);
    y = variable_name;
end