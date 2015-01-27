"""Manage a moving plot window for displaying very long time series."""
import time

class MovingPlotWindow:
    '''
    Make a plot window that follows the tip (end) of a very long
    time series.

    Here is an example where we have computed a long time series
    stored in an array ``u``. The time series is displayed by
    following a window of 8 periods. Along with ``u``, an
    analytical solution ``I*cos(w*t)`` is also plotted::

        import scitools.std as st
        from numpy import cos, pi
        from scitools.MovingPlotWindow import MovingPlotWindow

        def visualize_front(u, t, I, w):
            one_period = 2*pi/w
            umin = -1.2*I;  umax = -umin
            plot_manager = MovingPlotWindow(
                window_width=8*one_period,
                dt=t[1]-t[0],
                yaxis=[umin, umax],
                mode='continuous drawing')
            for n in range(1,len(u)):
                if plot_manager.plot(n):
                    s = plot_manager.first_index_in_plot
                    st.plot(t[s:n+1], u[s:n+1], 'r-',
                            t[s:n+1], I*cos(w*t)[s:n+1], 'b-',
                            title='t=%6.3f' % t[n],
                            axis=plot_manager.axis())
                plot_manager.update(n)

    Here is another example where the ``MovingPlotWindow`` object
    is used for plotting during the simulation::

        def demo(I, k, dt, T, mode='continuous movement'):
            """
            Solve u'' + k**2*u = 0, u(0)=I, u'(0)=0 by a finite
            difference method with time steps dt, from t=0 to t=T.
            """
            if dt > 2./k:
                print 'Unstable scheme'
            N = int(round(T/float(dt)))
            u = st.zeros(N+1)
            t = st.linspace(0, T, N+1)

            umin = -1.2*I
            umax = -umin
            period = 2*pi/k  # period of the oscillations
            window_width = 8*period
            plot_manager = MovingPlotWindow(
                             window_width, dt, yaxis=[umin, umax],
                             mode=mode)
            u[0] = I
            u[1] = u[0] - 0.5*dt**2*k**2*u[0]
            for n in range(1,N):
                u[n+1] = 2*u[n] - u[n-1] - dt**2*k**2*u[n]

                if plot_manager.plot(n):
                    s = plot_manager.first_index_in_plot
                    plot(t[s:n+2], u[s:n+2], 'r-',
                         t[s:n+2], I*cos(k*t)[s:n+2], 'b-',
                         axis=plot_manager.axis())
                plot_manager.update(n)
    '''

    def __init__(self, window_width, dt, yaxis=[-1,1],
                 mode='continuous movement',
                 pause=1.5):
        """
        ====================  ====================================
        Argument              Description
        ====================  ====================================
        window_width          tmax-tmin in a plot window
        dt                    time step (constant)
        yaxis                 extent of y axis
        mode                  method for moving the plot window,
                              see below.
        ====================  ====================================

        The mode parameter has three values:

          * ``'continuous movement'``:
            the plot window moves one time step for each plot.
          * ``'continuous drawing'``: the curves are drawn from left
            to right, one step at a time, and plot window jumps
            when the curve reaches the end.
          * ``'jumps'``: the curves are shown in a window for a time
            equal to the pause argument, then the axis jumps
            to a new time window of the same length


        See also the test block of the module for
        testing out the three different modes of this class.
        """
        self.taxis_length_in_steps = int(round(window_width/float(dt)))
        self.dt = dt
        self.mode = mode
        self.taxis_length = self.taxis_length_in_steps*self.dt
        self.first_index_in_plot = 0
        self.taxis_min = 0
        self.yaxis = yaxis
        self.pause = pause
        self.n_prev = 0

    def axis(self):
        """Return the axis limits as a list ``[xmin, xmax, ymin, ymax]``."""
        return [self.taxis_min, self.taxis_min + self.taxis_length,
                self.yaxis[0], self.yaxis[1]]

    def plot(self, n):
        """
        Return True if a plot is to be drawn at time step number ``n``,
        otherwise return False.
        """
        if self.mode == 'continuous movement':
            return True

        elif self.mode == 'continuous drawing':
            # Update self.first_index_in_plot and self.taxis_min
            # every self.taxis_length_in_steps time step
            if n % self.taxis_length_in_steps == 0:
                self.taxis_min += self.taxis_length
                self.first_index_in_plot += self.taxis_length_in_steps
            # Always plot the curves in continuous drawing
            return True
        else:
            # Plot every self.taxis_length_in_steps time step only
            if (n+1) % self.taxis_length_in_steps == 0:
                return True
            else:
                return False

    def update(self, n):
        """Update the plot manager (``MovingPlotWindow``) at time step `n`."""
        if self.mode == 'continuous movement':
            if n > self.taxis_length_in_steps:
                self.taxis_min += self.dt
                self.first_index_in_plot += n - self.n_prev
            self.n_prev = n

        elif self.mode == 'jumps' and \
               (n+1) % self.taxis_length_in_steps == 0:
            # After plot is shown, sleep and then update plot
            # window parameters
            time.sleep(self.pause)
            self.taxis_min += self.taxis_length
            self.first_index_in_plot += self.taxis_length_in_steps

def _demo(I, k, dt, T, mode='continuous movement'):
    """
    Solve u' = -k**2*u, u(0)=I, u'(0)=0 by a finite difference
    method with time steps dt, from t=0 to t=T.
    """
    if dt > 2./k:
        print 'Unstable scheme'
    N = int(round(T/float(dt)))
    u = zeros(N+1)
    t = linspace(0, T, N+1)

    umin = -1.2*I
    umax = -umin
    period = 2*pi/k  # period of the oscillations
    plot_manager = MovingPlotWindow(8*period, dt, yaxis=[umin, umax],
                                    mode=mode)
    u[0] = I
    u[1] = u[0] - 0.5*dt**2*k**2*u[0]
    for n in range(1,N):
        u[n+1] = 2*u[n] - u[n-1] - dt**2*k**2*u[n]

        if plot_manager.plot(n):
            s = plot_manager.first_index_in_plot
            plot(t[s:n+2], u[s:n+2], 'r-',
                 t[s:n+2], I*cos(k*t)[s:n+2], 'b-',
                 axis=plot_manager.axis(),
                 title="Solution of u'' + k^2 u = 0 for t=%6.3f (mode: %s)" \
                 % (t[n+1], mode))
        plot_manager.update(n)

if __name__ == '__main__':
    from scitools.std import *
    T = 40
    _demo(1, pi, 0.1, T, mode='continuous movement')
    time.sleep(10)
    figure()
    _demo(1, pi, 0.1, T, mode='continuous drawing')
    time.sleep(10)
    figure()
    _demo(1, pi, 0.1, T, mode='jumps')
    time.sleep(10)

