function add_data(name, value)
    evalin('base',strcat(name,'=',value,';'));
end