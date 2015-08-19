
def bokeh_plot(u, t, legends, u_e, t_e, I, w, t_range, filename):
    """
    Make plots for u vs t using the Bokeh library.
    u and t are lists (several experiments can be compared).
    legends contain legend strings for the various u,t pairs.
    Each plot has u vs t and the exact solution u_e vs t_e.
    """
    import numpy as np
    import bokeh.plotting as plt
    plt.output_file(filename, mode='cdn', title='Comparison')
    # Assume that all t arrays have the same range
    t_fine = np.linspace(0, t[0][-1], 1001)  # fine mesh for u_e
    tools = 'pan,wheel_zoom,box_zoom,reset,'\
            'save,box_select,lasso_select'
    u_range = [-1.2*I, 1.2*I]
    font_size = '8pt'
    p = []
    p_ = plt.figure(
        width=300, plot_height=250, title=legends[0],
        x_axis_label='t', y_axis_label='u',
        x_range=t_range, y_range=u_range, tools=tools,
        title_text_font_size=font_size)
    p_.xaxis.axis_label_text_font_size=font_size
    p_.yaxis.axis_label_text_font_size=font_size
    p_.line(t[0], u[0], line_color='blue')
    p_.line(t_e, u_e, line_color='red', line_dash='4 4')
    p.append(p_)
    for i in range(1, len(t)):
        p_ = plt.figure(
            width=300, plot_height=250, title=legends[i],
            x_axis_label='t', y_axis_label='u',
            x_range=p[0].x_range, y_range=p[0].y_range, tools=tools,
            title_text_font_size=font_size)
        p_.xaxis.axis_label_text_font_size=font_size
        p_.yaxis.axis_label_text_font_size=font_size
        p_.line(t[i], u[i], line_color='blue')
        p_.line(t_e, u_e, line_color='red', line_dash='4 4')
        p.append(p_)

    # Arrange in grid with 3 plots per row
    grid = [[]]
    for i, p_ in enumerate(p):
        grid[-1].append(p_)
        if (i+1) % 3 == 0:
            # New row
            grid.append([])
    plot = plt.gridplot(grid, toolbar_location='left')
    plt.save(plot)
    plt.show(plot)

def demo_bokeh():
    """Plot numerical and exact solution of sinousoidal shape."""
    import numpy as np

    def u_exact(t):
        return I*np.cos(w*t)

    def u_numerical(t):
        w_tilde = (2./dt)*np.arcsin(w*dt/2.)
        return I*np.cos(w_tilde*t)

    I = 1               # Amplitude
    w = 1.0             # Angular frequency
    P = 2*np.pi/w       # Period of signal
    num_steps_per_period = [5, 10, 20, 40, 80]
    num_periods = 40
    T = num_periods*P   # End time of signal

    t_e = np.linspace(0, T, 1001)  # Fine mesh for u_exact
    u_e = u_exact(t_e)
    u = []
    t = []
    legends = []

    # Make a series of numerical solutions with different time steps
    for n in num_steps_per_period:
        dt = P/n  # Time step length
        t_ = np.linspace(0, T, num_periods*n+1)
        u_ = u_numerical(t_)
        u.append(u_)
        t.append(t_)
        legends.append('# time steps per period: %d' % n)
    bokeh_plot(u, t, legends, u_e, t_e,
               I=1, w=w, t_range=[0, 4*P],
               filename='tmp.html')

demo_bokeh()
