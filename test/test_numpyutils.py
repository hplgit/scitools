allow_plot = True
from scitools.std import *

def test_PiecewiseConstant():
    data = [(0, 1.5), (3, 8), (4, 1)]
    f = PiecewiseConstant(domain=[0, 7],
                          data=data,
                          eps=0)
    b = [x for x, value in data]  # boundaries
    b.append(7)
    b = array(b)
    v = array([value for x, value in data])
    xm = array([0.5*(b[i-1] + b[i]) for i in range(1, len(b))]) # midpoints

    # Scalar vs array x in f(x)
    x = xm[0]
    assert allclose(f(xm), f(array(xm)))
    # Evaluations in the interior of domains
    assert allclose(f(xm), f._values)
    # Check boundary values: f(x[:-1]) = v, f(x[-1]) = v[-1]
    x = b
    y = zeros(len(v)+1)
    y[:-1] = v
    y[-1] = v[-1]
    assert allclose(f(x), y)

    if allow_plot:
        x = linspace(f.L, f.R, 31)    # no hit of boundaries
        y = f(x)
        x1, y1 = f.plot()
        n = 2
        x2 = linspace(f.L, f.R, n*7+1)  # hit of boundaries
        y2 = f(x2)
        plot(x, y, 'ro',
             x1, y1, 'b-',
             x2, y2, 'ko',
             legend=('f(x) w/no boundary pts in x', 'plot',
                     'f(x) w/boundary pts'),
             axis=[x[0], x[-1], 0, 10])

    f = PiecewiseConstant(domain=[0, 7],
                          data=data,
                          eps=0.5)

    # Scalar vs array x in f(x)
    x = xm[0]
    assert allclose(f(xm), f(array(xm)))
    # Evaluations in the interior of domains
    assert allclose(f(xm), f._values, atol=1E-6)
    # Check boundary values: mean values
    x = b
    y = zeros(len(v)+1)
    y[0] = v[0]
    y[1:-1] = 0.5*(v[:-1] + v[1:])
    y[-1] = v[-1]
    assert allclose(f(x), y)

    if allow_plot:
        figure()
        x = linspace(f.L, f.R, 31)    # no hit of boundaries
        y = f(x)
        x1, y1 = f.plot()
        n = 2
        x2 = linspace(f.L, f.R, n*7+1)  # hit of boundaries
        y2 = f(x2)
        plot(x, y, 'ro',
             x1, y1, 'b-',
             x2, y2, 'ko',
             legend=('f(x) w/no boundary pts in x', 'plot',
                     'f(x) w/boundary pts'),
             axis=[x[0], x[-1], 0, 10])

test_PiecewiseConstant()

