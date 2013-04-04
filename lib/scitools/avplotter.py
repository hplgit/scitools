"""
avplotter ("ascii vertical plotter") is a simple ASCII plotter for
curve plots, where the x axis points downward and the y axis
is horizontal. The plot is realized by printing it line by line.
There are two main applications: 1) very long time series, and
2) plots that would be convenient to have as pure text.

See the documentation of class Plotter for examples of various
types of plots.
"""

class Plotter:
    """
    ASCII plotter with x axis downwards and y axis horizontal.
    Can make a plot by writing out new x values line by line in a
    terminal window or a file.
    Very suited for long time series.

    Example:

    >>> a = 0.2
    >>> p = Plotter(-1-a, 1+a, width=50)
    >>> from math import sin, pi
    >>> from numpy import linspace
    >>> num_periods = 2
    >>> resolution_per_period = 22
    >>> tp = linspace(0, num_periods*2*pi,
    ...               num_periods*resolution_per_period + 1)
    >>> for t in tp:
    ...     y = (1 + a*sin(0.5*t))*sin(t)
    ...     print 't=%5.2f' % t, p.plot(t, y), '%5.2f' % y
    ...
    t= 0.00                          |                           0.00
    t= 0.29                          |     *                     0.29
    t= 0.57                          |           *               0.57
    t= 0.86                          |                *          0.82
    t= 1.14                          |                    *      1.01
    t= 1.43                          |                      *    1.12
    t= 1.71                          |                       *   1.14
    t= 2.00                          |                     *     1.06
    t= 2.28                          |                  *        0.89
    t= 2.57                          |            *              0.64
    t= 2.86                          |      *                    0.34
    t= 3.14                          |                           0.00
    t= 3.43                   *      |                          -0.34
    t= 3.71             *            |                          -0.64
    t= 4.00       *                  |                          -0.89
    t= 4.28    *                     |                          -1.06
    t= 4.57  *                       |                          -1.14
    t= 4.86   *                      |                          -1.12
    t= 5.14     *                    |                          -1.01
    t= 5.43         *                |                          -0.82
    t= 5.71              *           |                          -0.57
    t= 6.00                    *     |                          -0.29
    t= 6.28                          |                          -0.00
    t= 6.57                          |     *                     0.27
    t= 6.85                          |          *                0.51
    t= 7.14                          |             *             0.69
    t= 7.43                          |                *          0.81
    t= 7.71                          |                 *         0.86
    t= 8.00                          |                 *         0.84
    t= 8.28                          |               *           0.76
    t= 8.57                          |            *              0.62
    t= 8.85                          |        *                  0.44
    t= 9.14                          |    *                      0.23
    t= 9.42                          |                           0.00
    t= 9.71                     *    |                          -0.23
    t=10.00                 *        |                          -0.44
    t=10.28             *            |                          -0.62
    t=10.57          *               |                          -0.76
    t=10.85        *                 |                          -0.84
    t=11.14        *                 |                          -0.86
    t=11.42         *                |                          -0.81
    t=11.71            *             |                          -0.69
    t=12.00               *          |                          -0.51
    t=12.28                    *     |                          -0.27
    t=12.57                          |                          -0.00

    Here is a one-dimensional random walk example::

        import time, numpy as np
        p = Plotter(-1, 1, width=75)
        np.random.seed(10)
        y = 0
        while True:
            random_step = 1 if np.random.random() > 0.5 else -1
            y = y + 0.05*random_step
            if y < -1:
                print 'HOME!!!!!!!!!'
                break
            print p.plot(0, y)
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                print 'Interrupted by Ctrl-C'
                break

    One can easily plot two or more curves side by side. Here we
    plot two curves (sine and cosine), each with a width of 25
    characters::

        p_sin = Plotter(-1, 1, width=25, symbols='s')
        p_cos = Plotter(-1, 1, width=25, symbols='c')
        from math import sin, cos, pi
        from numpy import linspace
        tp = linspace(0, 6*pi, 6*8+1)
        for t in tp:
            print p_sin.plot(t, sin(t)), p_cos.plot(t, cos(t))

    The output reads::

                     |                          |           c
                     |   s                      |          c
                     |       s                  |       c
                     |          s               |   c
                     |           s              |
                     |          s          c    |
                     |       s         c        |
                     |   s          c           |
                     |             c            |
                s    |              c           |
            s        |                 c        |
         s           |                     c    |
        s            |                         c|
         s           |                          |   c
            s        |                          |       c
                s    |                          |          c
                    s|                          |           c
                     |   s                      |          c
                     |       s                  |       c
                     |          s               |   c
                     |           s              |
                     |          s          c    |
                     |       s         c        |
                     |   s          c           |
                     |             c            |
                s    |              c           |
            s        |                 c        |
         s           |                     c    |
        s            |                         c|
         s           |                          |   c
            s        |                          |       c
                s    |                          |          c
                    s|                          |           c
                     |   s                      |          c
                     |       s                  |       c
                     |          s               |   c
                     |           s              |
                     |          s          c    |
                     |       s         c        |
                     |   s          c           |
                     |             c            |
                s    |              c           |
            s        |                 c        |
         s           |                     c    |
        s            |                         c|
         s           |                          |   c
            s        |                          |       c
                s    |                          |          c
                    s|                          |           c

    Alternatively, two curves (here sine and cosine) can be
    plotted in the same coordinate system::

        p = Plotter(-1, 1, width=50, symbols='sc')
        from math import sin, cos, pi
        from numpy import linspace
        tp = linspace(0, 6*pi, 6*8+1)
        for t in tp:
            print p.plot(t, sin(t), cos(t))

    The output from this code becomes::

                                 |                        c
                                 |         s            c
                                 |                 c
                                 |         c            s
                                 |                        s
                       c         |                      s
               c                 |                 s
          c                      |         s
        c                        |
          c            s         |
               c                 |
          s            c         |
        s                        |
          s                      |         c
               s                 |                 c
                       s         |                      c
                                 |                        c
                                 |         s            c
                                 |                 c
                                 |         c            s
                                 |                        s
                       c         |                      s
               c                 |                 s
          c                      |         s
        c                        |
          c            s         |
               c                 |
          s            c         |
        s                        |
          s                      |         c
               s                 |                 c
                       s         |                      c
                                 |                        c
                                 |         s            c
                                 |                 c
                                 |         c            s
                                 |                        s
                       c         |                      s
               c                 |                 s
          c                      |         s
        c                        |
          c            s         |
               c                 |
          s            c         |
        s                        |
          s                      |         c
               s                 |                 c
                       s         |                      c
                                 |                        c


    """
    def __init__(self, ymin, ymax, width=68, symbols='*o+x@',
                 vertical_line=0):
        """
        Create a line by line plotter with the x axis pointing
        downward. The `ymin` and `ymax` variables define the
        extent of the y axis. The `width` parameter is the number
        of characters used for the y domain (axis). The symbols
        used for curves are given by the `symbols` string
        (first symbol, by default is ``*``, next is ``o``).
        The `vertical_line` parameter specifies for which y value
        where the x axis is drawn (y=0 by default).
        """

        self.yaxis = float(ymin), float(ymax)
        self.width = width
        self.symbols = symbols
        self.vertical_line = vertical_line

    def _map(self, y):
        """Return the column no. corresponding to y."""
        ymin, ymax = self.yaxis

        if   y < ymin:
            self.too_small = True
            self.too_large = False
            c = 0
        elif y > ymax:
            self.too_small = False
            self.too_large = True
            c = -1
        else:
            self.too_small = self.too_large = False
            y_in_01 = (y-ymin)/(ymax - ymin)
            c = int(round(y_in_01*self.width))
        return c

    def plot(self, x, *y, **kwargs):
        """
        Return next line in plot, given x and some y values.

        Supported kwargs:
        print_out_of_range_value: if True, print the value if it
        is out of range.

        """
        print_out_of_range_value = \
              kwargs.get('print_out_of_range_value', True)
        line = [' ']*(self.width + 1)
        y_value = ''
        for yi, symbol in zip(y, self.symbols):
            c = self._map(yi)
            if self.too_small or self.too_large:
                symbol = '|'
                if print_out_of_range_value:
                    y_value = '%.1E' % yi
            else:
                line[c] = symbol

        # Mark 'x' axis
        if self.yaxis[0] < self.vertical_line and \
           self.yaxis[1] > self.vertical_line:
            c = self._map(0)
            line[c] = '|'
        return ''.join(line) + y_value


def plot(*args, **kwargs):
    """
    Easyviz-style plot command.
    args holds x1, y1, x2, y2, ...::

      plot(t, u1, t, u2, axis=[0, 10, -1, 1])

    No other keyword arguments has any effect.
    """
    if 'axis' in kwargs:
        ymin, ymax = kwargs['axis'][2:]
    else:
        ymin = 1E+20
        ymax = -ymin
        for i in range(1,len(args),2):
            ymin = max(ymin, args[i].min())
            ymax = max(ymax, args[i].max())
    p = Plotter(ymin, ymax, width=70)
    num_curves = len(args)/2
    if num_curves > 4:
        raise ValueError('avplotter.plot: cannot plot more than 4 curves')

    x_length = len(args[0])
    for i in range(2,len(args),2):
        if len(args[i]) != x_length:
            raise ValueError('avplotter.plot: all x coordinates for all curves must have the same length (%d vs %d)' % (len(args[i]), x_length))

    x_array = args[0]
    for i, x in enumerate(x_array):
        try:
            y = [args[j][i] for j in range(1,len(args),2)]
        except IndexError:
            raise ValueError('index %d in x_array is illegal in args[%d] (length=%d)' % (i, j, len(args[j])))

        print p.plot(x_array, *y)


def test_sin():
    a = 0.2
    p = Plotter(-1-a, 1+a, width=50)
    from math import sin, pi
    from numpy import linspace
    num_periods = 2
    resolution_per_period = 22
    s = ''
    tp = linspace(0, num_periods*2*pi,
                  num_periods*resolution_per_period + 1)
    for t in tp:
        y = (1 + a*sin(0.5*t))*sin(t)
        s += 't=%5.2f %s %5.2f\n' % (t, p.plot(t, y), y)

    ans = """\
t= 0.00                          |                           0.00
t= 0.29                          |     *                     0.29
t= 0.57                          |           *               0.57
t= 0.86                          |                *          0.82
t= 1.14                          |                    *      1.01
t= 1.43                          |                      *    1.12
t= 1.71                          |                       *   1.14
t= 2.00                          |                     *     1.06
t= 2.28                          |                  *        0.89
t= 2.57                          |            *              0.64
t= 2.86                          |      *                    0.34
t= 3.14                          |                           0.00
t= 3.43                   *      |                          -0.34
t= 3.71             *            |                          -0.64
t= 4.00       *                  |                          -0.89
t= 4.28    *                     |                          -1.06
t= 4.57  *                       |                          -1.14
t= 4.86   *                      |                          -1.12
t= 5.14     *                    |                          -1.01
t= 5.43         *                |                          -0.82
t= 5.71              *           |                          -0.57
t= 6.00                    *     |                          -0.29
t= 6.28                          |                          -0.00
t= 6.57                          |     *                     0.27
t= 6.85                          |          *                0.51
t= 7.14                          |             *             0.69
t= 7.43                          |                *          0.81
t= 7.71                          |                 *         0.86
t= 8.00                          |                 *         0.84
t= 8.28                          |               *           0.76
t= 8.57                          |            *              0.62
t= 8.85                          |        *                  0.44
t= 9.14                          |    *                      0.23
t= 9.42                          |                           0.00
t= 9.71                     *    |                          -0.23
t=10.00                 *        |                          -0.44
t=10.28             *            |                          -0.62
t=10.57          *               |                          -0.76
t=10.85        *                 |                          -0.84
t=11.14        *                 |                          -0.86
t=11.42         *                |                          -0.81
t=11.71            *             |                          -0.69
t=12.00               *          |                          -0.51
t=12.28                    *     |                          -0.27
t=12.57                          |                          -0.00
"""
    assert _compare(ans, s)

def test_2_curves_v1():
    p_sin = Plotter(-1, 1, width=25, symbols='s')
    p_cos = Plotter(-1, 1, width=25, symbols='c')
    from math import sin, cos, pi
    from numpy import linspace
    tp = linspace(0, 6*pi, 6*8+1)
    s = ''
    for t in tp:
        s += '%s %s\n' % (p_sin.plot(t, sin(t)), p_cos.plot(t, cos(t)))
    ans = """\
             |                          |           c
             |   s                      |          c
             |       s                  |       c
             |          s               |   c
             |           s              |
             |          s          c    |
             |       s         c        |
             |   s          c           |
             |             c            |
        s    |              c           |
    s        |                 c        |
 s           |                     c    |
s            |                         c|
 s           |                          |   c
    s        |                          |       c
        s    |                          |          c
            s|                          |           c
             |   s                      |          c
             |       s                  |       c
             |          s               |   c
             |           s              |
             |          s          c    |
             |       s         c        |
             |   s          c           |
             |             c            |
        s    |              c           |
    s        |                 c        |
 s           |                     c    |
s            |                         c|
 s           |                          |   c
    s        |                          |       c
        s    |                          |          c
            s|                          |           c
             |   s                      |          c
             |       s                  |       c
             |          s               |   c
             |           s              |
             |          s          c    |
             |       s         c        |
             |   s          c           |
             |             c            |
        s    |              c           |
    s        |                 c        |
 s           |                     c    |
s            |                         c|
 s           |                          |   c
    s        |                          |       c
        s    |                          |          c
            s|                          |           c
"""
    assert _compare(ans, s)

def test_2_curves_v2():
    p = Plotter(-1, 1, width=50, symbols='sc')
    from math import sin, cos, pi
    from numpy import linspace
    tp = linspace(0, 6*pi, 6*8+1)
    s = ''
    for t in tp:
        s += '%s\n' % (p.plot(t, sin(t), cos(t)))
    ans = """\
                         |                        c
                         |         s            c
                         |                 c
                         |         c            s
                         |                        s
               c         |                      s
       c                 |                 s
  c                      |         s
c                        |
  c            s         |
       c                 |
  s            c         |
s                        |
  s                      |         c
       s                 |                 c
               s         |                      c
                         |                        c
                         |         s            c
                         |                 c
                         |         c            s
                         |                        s
               c         |                      s
       c                 |                 s
  c                      |         s
c                        |
  c            s         |
       c                 |
  s            c         |
s                        |
  s                      |         c
       s                 |                 c
               s         |                      c
                         |                        c
                         |         s            c
                         |                 c
                         |         c            s
                         |                        s
               c         |                      s
       c                 |                 s
  c                      |         s
c                        |
  c            s         |
       c                 |
  s            c         |
s                        |
  s                      |         c
       s                 |                 c
               s         |                      c
                         |                        c
"""
    assert _compare(ans, s)

def test_random_walk():
    import time, numpy as np
    p = Plotter(-1, 1, width=75)
    np.random.seed(10)
    y = 0
    s = ''
    while True:
        random_step = 1 if np.random.random() > 0.5 else -1
        y = y + 0.05*random_step
        if y < -1:
            break
        s += '%s\n' % (p.plot(0, y))  # t is just dummy
    ans = """\
                                      |*
                                      |
                                      |*
                                      |  *
                                      |*
                                      |
                                    * |
                                      |
                                    * |
                                  *   |
                                    * |
                                      |
                                    * |
                                      |
                                      |*
                                      |  *
                                      |    *
                                      |  *
                                      |    *
                                      |      *
                                      |        *
                                      |      *
                                      |    *
                                      |      *
                                      |    *
                                      |  *
                                      |    *
                                      |      *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |               *
                                      |              *
                                      |            *
                                      |          *
                                      |        *
                                      |          *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |        *
                                      |      *
                                      |        *
                                      |      *
                                      |    *
                                      |      *
                                      |        *
                                      |      *
                                      |        *
                                      |      *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |        *
                                      |      *
                                      |    *
                                      |      *
                                      |    *
                                      |  *
                                      |*
                                      |  *
                                      |*
                                      |
                                      |*
                                      |  *
                                      |    *
                                      |  *
                                      |    *
                                      |      *
                                      |        *
                                      |      *
                                      |    *
                                      |  *
                                      |*
                                      |
                                      |*
                                      |  *
                                      |*
                                      |
                                    * |
                                      |
                                    * |
                                  *   |
                                    * |
                                  *   |
                                *     |
                                  *   |
                                    * |
                                      |
                                    * |
                                  *   |
                                    * |
                                      |
                                      |*
                                      |
                                    * |
                                      |
                                    * |
                                      |
                                      |*
                                      |
                                    * |
                                  *   |
                                *     |
                              *       |
                                *     |
                              *       |
                            *         |
                              *       |
                            *         |
                              *       |
                            *         |
                              *       |
                            *         |
                          *           |
                            *         |
                          *           |
                        *             |
                          *           |
                        *             |
                       *              |
                        *             |
                          *           |
                            *         |
                              *       |
                            *         |
                              *       |
                                *     |
                                  *   |
                                    * |
                                      |
                                      |*
                                      |  *
                                      |*
                                      |
                                      |*
                                      |
                                    * |
                                  *   |
                                    * |
                                      |
                                    * |
                                      |
                                      |*
                                      |  *
                                      |*
                                      |
                                    * |
                                  *   |
                                *     |
                              *       |
                                *     |
                                  *   |
                                *     |
                              *       |
                                *     |
                                  *   |
                                    * |
                                      |
                                      |*
                                      |  *
                                      |    *
                                      |  *
                                      |    *
                                      |  *
                                      |*
                                      |  *
                                      |*
                                      |  *
                                      |*
                                      |
                                      |*
                                      |  *
                                      |*
                                      |
                                    * |
                                  *   |
                                *     |
                                  *   |
                                *     |
                              *       |
                                *     |
                              *       |
                                *     |
                                  *   |
                                *     |
                              *       |
                                *     |
                                  *   |
                                *     |
                                  *   |
                                *     |
                              *       |
                                *     |
                                  *   |
                                    * |
                                      |
                                    * |
                                      |
                                      |*
                                      |
                                      |*
                                      |
                                    * |
                                  *   |
                                *     |
                              *       |
                            *         |
                              *       |
                            *         |
                          *           |
                            *         |
                          *           |
                        *             |
                          *           |
                        *             |
                          *           |
                        *             |
                          *           |
                            *         |
                              *       |
                                *     |
                              *       |
                            *         |
                          *           |
                            *         |
                              *       |
                            *         |
                          *           |
                            *         |
                          *           |
                        *             |
                          *           |
                            *         |
                          *           |
                            *         |
                          *           |
                            *         |
                          *           |
                            *         |
                              *       |
                                *     |
                              *       |
                            *         |
                              *       |
                                *     |
                                  *   |
                                *     |
                              *       |
                            *         |
                              *       |
                                *     |
                              *       |
                            *         |
                              *       |
                                *     |
                                  *   |
                                    * |
                                      |
                                      |*
                                      |
                                    * |
                                  *   |
                                    * |
                                  *   |
                                    * |
                                  *   |
                                    * |
                                  *   |
                                    * |
                                      |
                                    * |
                                  *   |
                                    * |
                                  *   |
                                *     |
                              *       |
                            *         |
                              *       |
                            *         |
                              *       |
                                *     |
                                  *   |
                                    * |
                                      |
                                    * |
                                  *   |
                                    * |
                                  *   |
                                    * |
                                      |
                                      |*
                                      |
                                    * |
                                  *   |
                                    * |
                                      |
                                    * |
                                      |
                                      |*
                                      |
                                      |*
                                      |  *
                                      |    *
                                      |  *
                                      |*
                                      |
                                      |*
                                      |
                                    * |
                                      |
                                    * |
                                  *   |
                                    * |
                                      |
                                    * |
                                  *   |
                                    * |
                                  *   |
                                *     |
                                  *   |
                                    * |
                                      |
                                      |*
                                      |
                                      |*
                                      |  *
                                      |    *
                                      |      *
                                      |        *
                                      |          *
                                      |        *
                                      |          *
                                      |        *
                                      |      *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |               *
                                      |              *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |               *
                                      |              *
                                      |            *
                                      |          *
                                      |        *
                                      |      *
                                      |    *
                                      |      *
                                      |    *
                                      |      *
                                      |    *
                                      |  *
                                      |*
                                      |  *
                                      |    *
                                      |      *
                                      |        *
                                      |          *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |               *
                                      |              *
                                      |            *
                                      |              *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |              *
                                      |               *
                                      |              *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                                *
                                      |                              *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                              *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                                  *
                                      |                                     1.0E+00
                                      |                                     1.1E+00
                                      |                                     1.1E+00
                                      |                                     1.1E+00
                                      |                                     1.0E+00
                                      |                                  *
                                      |                                *
                                      |                              *
                                      |                                *
                                      |                                  *
                                      |                                     1.0E+00
                                      |                                     1.1E+00
                                      |                                     1.0E+00
                                      |                                     1.1E+00
                                      |                                     1.1E+00
                                      |                                     1.1E+00
                                      |                                     1.0E+00
                                      |                                  *
                                      |                                     1.0E+00
                                      |                                  *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                              *
                                      |                                *
                                      |                              *
                                      |                                *
                                      |                              *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |               *
                                      |              *
                                      |            *
                                      |          *
                                      |        *
                                      |          *
                                      |        *
                                      |          *
                                      |        *
                                      |          *
                                      |        *
                                      |          *
                                      |            *
                                      |          *
                                      |            *
                                      |          *
                                      |            *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |              *
                                      |               *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |        *
                                      |          *
                                      |        *
                                      |      *
                                      |    *
                                      |  *
                                      |    *
                                      |      *
                                      |        *
                                      |          *
                                      |        *
                                      |          *
                                      |        *
                                      |      *
                                      |        *
                                      |      *
                                      |        *
                                      |          *
                                      |        *
                                      |      *
                                      |        *
                                      |      *
                                      |    *
                                      |      *
                                      |    *
                                      |  *
                                      |*
                                     *|
                                    * |
                                  *   |
                                *     |
                              *       |
                            *         |
                          *           |
                        *             |
                      *               |
                        *             |
                          *           |
                            *         |
                          *           |
                            *         |
                          *           |
                            *         |
                              *       |
                                *     |
                              *       |
                                *     |
                                  *   |
                                    * |
                                  *   |
                                *     |
                              *       |
                                *     |
                                  *   |
                                *     |
                                  *   |
                                    * |
                                     *|
                                      |*
                                      |  *
                                      |    *
                                      |  *
                                      |    *
                                      |      *
                                      |    *
                                      |      *
                                      |    *
                                      |  *
                                      |*
                                      |  *
                                      |*
                                     *|
                                    * |
                                  *   |
                                *     |
                                  *   |
                                *     |
                              *       |
                            *         |
                              *       |
                                *     |
                                  *   |
                                    * |
                                     *|
                                      |*
                                     *|
                                    * |
                                     *|
                                    * |
                                     *|
                                      |*
                                     *|
                                    * |
                                  *   |
                                *     |
                                  *   |
                                    * |
                                  *   |
                                    * |
                                     *|
                                    * |
                                     *|
                                    * |
                                     *|
                                      |*
                                     *|
                                      |*
                                     *|
                                    * |
                                     *|
                                      |*
                                      |  *
                                      |    *
                                      |  *
                                      |    *
                                      |  *
                                      |    *
                                      |  *
                                      |*
                                      |  *
                                      |*
                                      |  *
                                      |*
                                      |  *
                                      |    *
                                      |      *
                                      |        *
                                      |          *
                                      |        *
                                      |      *
                                      |    *
                                      |      *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |               *
                                      |              *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                                *
                                      |                                  *
                                      |                                     1.0E+00
                                      |                                  *
                                      |                                *
                                      |                              *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                              *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                                  *
                                      |                                     1.0E+00
                                      |                                     1.1E+00
                                      |                                     1.0E+00
                                      |                                  *
                                      |                                *
                                      |                                  *
                                      |                                *
                                      |                              *
                                      |                             *
                                      |                              *
                                      |                             *
                                      |                              *
                                      |                                *
                                      |                              *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |              *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |               *
                                      |                 *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |            *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |          *
                                      |        *
                                      |          *
                                      |            *
                                      |              *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |                   *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |               *
                                      |                 *
                                      |                   *
                                      |                     *
                                      |                       *
                                      |                     *
                                      |                       *
                                      |                         *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                         *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                             *
                                      |                           *
                                      |                         *
                                      |                           *
                                      |                         *
                                      |                       *
                                      |                     *
                                      |                   *
                                      |                     *
                                      |                   *
                                      |                 *
                                      |               *
                                      |              *
                                      |               *
                                      |              *
                                      |               *
                                      |              *
                                      |            *
                                      |          *
                                      |            *
                                      |          *
                                      |            *
                                      |          *
                                      |            *
                                      |          *
                                      |        *
                                      |      *
                                      |    *
                                      |  *
                                      |*
                                      |  *
                                      |*
                                     *|
                                    * |
                                  *   |
                                    * |
                                     *|
                                      |*
                                      |  *
                                      |*
                                     *|
                                    * |
                                  *   |
                                *     |
                              *       |
                            *         |
                              *       |
                            *         |
                          *           |
                            *         |
                          *           |
                        *             |
                          *           |
                        *             |
                          *           |
                        *             |
                      *               |
                        *             |
                      *               |
                        *             |
                      *               |
                        *             |
                          *           |
                            *         |
                              *       |
                            *         |
                              *       |
                            *         |
                              *       |
                                *     |
                              *       |
                            *         |
                          *           |
                        *             |
                      *               |
                        *             |
                      *               |
                     *                |
                   *                  |
                 *                    |
               *                      |
             *                        |
           *                          |
         *                            |
           *                          |
             *                        |
           *                          |
             *                        |
               *                      |
             *                        |
           *                          |
             *                        |
               *                      |
             *                        |
           *                          |
         *                            |
       *                              |
      *                               |
    *                                 |
  *                                   |
    *                                 |
      *                               |
       *                              |
      *                               |
       *                              |
      *                               |
       *                              |
      *                               |
    *                                 |
  *                                   |
    *                                 |
      *                               |
       *                              |
      *                               |
    *                                 |
  *                                   |
    *                                 |
      *                               |
    *                                 |
      *                               |
    *                                 |
      *                               |
       *                              |
         *                            |
           *                          |
         *                            |
           *                          |
         *                            |
       *                              |
         *                            |
       *                              |
         *                            |
           *                          |
             *                        |
               *                      |
                 *                    |
                   *                  |
                 *                    |
               *                      |
             *                        |
           *                          |
         *                            |
           *                          |
         *                            |
           *                          |
             *                        |
               *                      |
             *                        |
           *                          |
             *                        |
           *                          |
             *                        |
           *                          |
         *                            |
       *                              |
         *                            |
       *                              |
         *                            |
           *                          |
         *                            |
       *                              |
         *                            |
           *                          |
             *                        |
               *                      |
                 *                    |
               *                      |
                 *                    |
               *                      |
             *                        |
           *                          |
         *                            |
       *                              |
         *                            |
           *                          |
         *                            |
           *                          |
         *                            |
       *                              |
         *                            |
           *                          |
             *                        |
           *                          |
             *                        |
               *                      |
             *                        |
           *                          |
         *                            |
           *                          |
             *                        |
           *                          |
         *                            |
           *                          |
             *                        |
           *                          |
             *                        |
           *                          |
         *                            |
       *                              |
      *                               |
    *                                 |
  *                                   |
"""
    assert _compare(ans, s)

def run_random_walk():
    import time, numpy as np
    p = Plotter(-1, 1, width=75)
    np.random.seed(10)
    y = 0
    while True:
        random_step = 1 if np.random.random() > 0.5 else -1
        y = y + 0.05*random_step
        if y < -1:
            print 'HOME!!!'
            break
        print p.plot(0, y)
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print 'Interrupted by Ctrl-C'
            break

def _compare(ans, s):
    for line1, line2 in zip(ans.splitlines(), s.splitlines()):
        if line1.strip() != line2.strip():
            return False
    return True

if __name__ == '__main__':
    import sys
    try:
        if sys.argv[1] == 'random_walk':
            run_random_walk()
    except:
        pass
