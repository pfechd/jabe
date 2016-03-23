function plot_data(data)
    p = evalin('base', data);
    plot(p);
end