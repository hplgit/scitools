#!/usr/bin/env python
'''
Module for estimating convergence rate of numerical algorithms,
based on data from a set of experiments.

It is recommended to vary only
one discretization parameter h. In spatial problems, h is the mesh
spacing dx, dy, or dz.
In time-dependent problems, where the expected convergence rate is
h^p + dt^q, choose h^p/dt^q = const.
Use class ``OneDiscretizationPrm``, or the function ``convergence_rate``,
or the ``analyze_filedata`` convenience function.

Here is a simple example::

    h = [0.2, 0.1, 0.05, 0.025]  # discretization parameters
    e = [compute_error(hi) for hi in h]

    rates, C = OneDiscretizationPrm.pairwise_rates(h, e)
    print C, rates  # see if rates converges
    print 'final rate:', rates[-1]

There is support for fitting more general error models, like
C1*h^r1 + C2*h*dt^r2, with nonlinear least squares, but in that case it
is more challenging to find sound fits.
'''

from scitools.misc import import_module
from numpy import zeros, array, asarray, log10, transpose, linalg, linspace
import sys
from scitools.std import plot

__all__ = ['ManyDiscretizationPrm',
           'OneDiscretizationPrm',
           ]

log = log10
inv_log = lambda x: 10**x

# The classes in this module have only static methods, i.e.,
# classes are merely name spaces for related functions.


class OneDiscretizationPrm(object):
    """
    Tools for fitting an error model with only one discretization
    parameter: e = C*h^2.
    """

    def error_model(p, d):
        """Return e = C*h**a, where p=[C, a] and h=d[0]."""
        C, a = p
        h = d[0]
        return C*h**a

    def loglog_error_model(p, d):
        """As ``error_model``, but log-log data was used in the estimation."""
        C, a = p
        h = d[0]
        return log(C) + a*log(h)


    def linear_loglog_fit(d, e):
        """
        Linear least squares algorithm.
        Suitable for problems with only one distinct
        discretization parameter.
        `d` is the sequence of discretization parameter values, and
        `e` is the sequence of corresponding error values.

        The error model the data is supposed to fit reads
        ``log(e[i]) = log(C[i]) + a*log(d[i])``.
        """
        A = transpose(array([d, zeros(len(d))+1]))
        sol = linalg.lstsq(A, e)
        a, logC = sol[0]
        C = inv_log(logC)
        return a, C

    def nonlinear_fit(d, e, p0):
        """
        ======== ===========================================================
        Name     Description
        ======== ===========================================================
        d        list of values of the (single) discretization
                 parameter in each experiment:
                 ``d[i]`` provides the values of the discretization,
                 parameter in experiement no. i.
        e        list of error values; ``e = (e_1, e_2, ...)``,
                 ``e[i]`` is the error associated with the parameters
                 ``d[i]``
        p0       starting values for the unknown parameters vector
        return   r, C; r is the exponent, C is the factor in front
        ======== ===========================================================
        """
        if len(d) != len(e):
            raise ValueError('d and e must have the same length')
        if not isinstance(d[0], (float,int)):
            raise TypeError('d must be an array of numbers, not %s' % \
                            str(type(d[0])))
        # transform d and e to the data format required by
        # the Scientific package:
        data = []
        for d_i, e_i in zip(d, e):
            data.append(((d_i,) , e_i))  # recall (a,) conversion to tuple
        leastSquaresFit = import_module('Scientific.Functions.LeastSquares',
                                        'leastSquaresFit')
        sol = leastSquaresFit(OneDiscretizationPrm.error_model, p0, data)
        C = sol[0][0]
        a = sol[0][1]
        return a, C


    def pairwise_rates(d, e):
        """
        Compare convergence rates, where each rate is based on
        a formula for two successive experiments.
        """
        if len(d) != len(e):
            raise ValueError('d and e must have the same length')

        rates = []
        for i in range(1, len(d)):
            try:
                rates.append( log(e[i-1]/e[i])/log(float(d[i-1])/d[i]) )
            except (ZeroDivisionError, OverflowError):
                rates.append(0)
        # estimate C from the last data point:
        try:
            C = e[-1]/d[-1]**rates[-1]
        except:
            C = 0
        return rates, C


    def analyze(d, e, initial_guess=None,
                plot_title='', filename='tmp.ps'):
        """
        Run linear, nonlinear and successive rates models.
        Plot results for comparison of the three approaches.

        ============== =================================================
        Argument       Description
        ============== =================================================
        d              list/array of discretization parameter
        e              errors corresponding to d
        initial_guess  estimate of convergence rate parameters
        plot_title     title in plot
        filename       name of plot file
        ============== =================================================
        """
        # convert to NumPy arrays:
        d = asarray(d, float);  e = asarray(e, float)

        # linear least squares fit:
        a1, C1 = OneDiscretizationPrm.linear_loglog_fit(log(d), log(e))
        print "linear LS fit: const=%e rate=%.1f" % (C1, a1)

        # nonlinear least squares fit (no log-log):
        a2, C2 = OneDiscretizationPrm.nonlinear_fit(d, e, initial_guess)
        print "nonlinear LS fit: const=%e rate=%.1f" % (C2, a2)

        # pairwise estimate of the rate:
        rates, C3 = OneDiscretizationPrm.pairwise_rates(d, e)
        a3 = rates[-1]
        print "pairwise fit: const=%e rate=%.1f" % (C3, a3)
        print "all rates:", rates

        if C1 < 0 or C2 < 0 or C3 < 0:
            raise ValueError('Some fits give negative const value! Cannot plot.')
            return

        # else log plot:
        log_d1 = linspace(log(d[0]), log(d[-1]), 2)
        log_e1 = log(C1) + a1*log_d1
        log_e2 = log(C2) + a2*log_d1
        log_e3 = log(C3) + a3*log_d1
        plot(log(d), log(e), 'yo',
             log_d1, log_e1, 'r-',
             log_d1, log_e2, 'b-',
             log_d1, log_e3, 'g-',
             legend=('data',
                     'linear LS log-log fit: %.1f*h^%.1f' % (log(C1), a1),
                     'nonlinear LS fit: %.1f*h^%.1f' % (log(C2), a2),
                     'successive rates, last two experiments: %.1f*h^%.1f' % (log(C3), a3)),
             #axis=[log_d1[-1], log_d1[0], 1.3*log(e[-1]), 1.5*log(e[0])],
             hardcopy=filename)

    analyze = staticmethod(analyze)

    error_model = staticmethod(error_model)
    loglog_error_model = staticmethod(loglog_error_model)
    linear_loglog_fit = staticmethod(linear_loglog_fit)
    nonlinear_fit = staticmethod(nonlinear_fit)
    pairwise_rates = staticmethod(pairwise_rates)

# convenience function:
def convergence_rate(discretization_prm, error):
    """
    Given two lists/arrays with discretization parameters and
    corresponding errors in a numerical method (element no. i
    in the two lists must correspond to each other), this
    function assumes an error formula of the form E=C*d^r,
    where E is the error and d is the discretization parameter.
    The function returns C and r.

    Method used: OneDiscretizationPrm.pairwise_rates is called
    and the final r value is used for return. A check that
    the rates are converging (the last three) is done.
    """
    rates, C = OneDiscretizationPrm.pairwise_rates(discretization_prm, error)
    # check that there is no divergence at the end of
    # the series of experiments
    differences = [rates[i] - rates[i-1] for i in range(len(rates)-1)]
    # the differences between the rates should decrease, at least
    # toward the end
    try:
        if differences[-1] > differences[-2]:
            raise ValueError('The pairwise convergence rates do not '\
                             'decrease toward the end:\n%s' % \
                             str(rates))
    except IndexError:
        pass  # not enough data to check the differences list
    return C, rates[-1]

class ManyDiscretizationPrm(object):
    """
    General tool for fitting an error model containing an
    arbitrary number of discretization parameters.
    The error is a weighted sum of each discretization parameter
    raised to a real expoenent. The weights and exponents are
    the unknown parameters to be fitted by a nonlinear
    least squares procedure.
    """

    def error_model(p, d):
        """
        Evaluate the theoretical error model (sum of C*h^r terms):
        sum_i p[2*i]*d[i]**p[2*i+1]

        ====== =======================================================
        Name   Description
        ====== =======================================================
        p      sequence ofvalues of  parameters (estimated)
        d      sequence of values of (known) discretization parameters
        return error evaluated
        ====== =======================================================

        Note that ``len(p)`` must be ``2*len(d)`` in this model since
        there are two parameters (constant and exponent) for each
        discretization parameter.
        """
        if len(p) != 2*len(d):
            raise ValueError('len(p)=%d != 2*len(d)=%d' % (len(p),2*len(d)))
        sum = 0
        for i in range(len(d)):
            sum += p[2*i] * d[i]**p[2*i+1]
        return sum

    def nonlinear_fit(d, e, initial_guess):
        """
        ============== ================================================
        Argument       Description
        ============== ================================================
        d              list of values of the set of discretization
                       parameters in each experiment:
                       ``d = ((d_1,d_2,d_3),(d_1,d_2,d_3,),...)``;
                       ``d[i]`` provides the values of the
                       discretization parameters in experiement no. i.
        e              list of error values; ``e = (e_1, e_2, ...)``:
                       ``e[i]`` is the error associated with the
                       parameters ``d[i]``
        initial_guess  the starting value for the unknown
                       parameters vector
        return         list of fitted parameters
        ============== ================================================
        """
        if len(d) != len(e):
            raise ValueError('len(d) != len(e)')
        # transform d and e to the data format required by
        # the Scientific package:
        data = []
        for d_i, e_i in zip(d, e):
            if isinstance(d_i, (float, int)):
                data.append(((d_i,), e_i))
            else:  # d_i is tuple, list, array, NumArray, ...
                data.append((d_i, e_i))
        leastSquaresFit = import_module('Scientific.Functions.LeastSquares',
                                        'leastSquaresFit')
        sol = leastSquaresFit(ManyDiscretizationPrm.error_model,
                              initial_guess, data)
        # return list of fitted parameters (p in error_model)
        # (sol[1] is a measure of the quality of the fit)
        return sol[0]

    error_model = staticmethod(error_model)
    nonlinear_fit = staticmethod(nonlinear_fit)


def _test1():
    """Single discretization parameter test."""
    import random
    random.seed(1234)
    n = 7
    h = 1
    e = [];  d = []
    for i in range(7):
        h /= 2.0
        error = OneDiscretizationPrm.error_model((4,2), (h,))
        error += random.gauss(0, 0.1*error)  # perturb data
        d.append(h)
        e.append(error)
    OneDiscretizationPrm.analyze(d, e, initial_guess=(3,2))

def analyze_filedata():
    """
    Reads ``f C r`` from the command line, where ``f`` is the name of
    a file, ``C`` and ``r`` are the initial guesses of the parameters
    in the error model E = C*h^r. A 4th command-line argument can be
    the plot title.
    """
    # read filename and initial guess of C and r in error formula E=C*h^r
    f = open(sys.argv[1], 'r')
    C = float(sys.argv[2])
    r = float(sys.argv[3])
    try:
        plot_title = sys.argv[4]
    except:
        plot_title = ''
    from scitools.filetable import read
    data = read(f)
    print data
    OneDiscretizationPrm.analyze(data[:,0], data[:,1],
                                 initial_guess=(C,r),
                                 plot_title=plot_title)

# extensions:
# example with dx, dy and dt
# same example, but with factors to get a common rate
# dx, dt tables and experiments with whole table, one
# column and one row, and the diagonal

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: %s filename C-guess r-guess [plot-title]' % sys.argv[0]
    elif sys.argv[1] == 'example':
        _test1()
    else:
        analyze_filedata()
