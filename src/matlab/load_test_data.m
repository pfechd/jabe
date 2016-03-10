function load_test_data()
    s = what('test-data/');
    matfiles = s.mat;
    
    for a=1:numel(matfiles)
        v = load(strcat('test-data/', char(matfiles(a))));
        s = fieldnames(v);
        set_data(char(s), v.(s{:}));
    end
end