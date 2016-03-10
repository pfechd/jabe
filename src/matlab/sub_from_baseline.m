function y = sub_from_baseline(data)
    % This function takes the first value from data and subtracts it from the rest.
    % Input/Output: Braindata array

    %------------------------------------------
    %Dubbel kod, finns i plot. Om jag kan anta att jag får in response1_std som inparameter så kan denna bit tas bort
    data = evalin('base', data);

    antalBilder = size(data,2);

    for b1 = 1:antalBilder
        rm1 = find(data(:,b1));
        response1_std(b1) = std(data(rm1,b1));
    end
    %------------------------------------------

    sub_value = response1_std(1);

    for b2 = 1:antalBilder
        sub_response1_std(b2) = response1_std(b2) - sub_value;
    end

    y = sub_response1_std;
end