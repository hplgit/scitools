#!/usr/bin/env python
"""
Module for estimating convergence rate of numerical algorithms,
based on data from a set of experiments.
"""

from Scientific.Functions.LeastSquares import leastSquaresFit
from scitools.numpytools import *
import Gnuplot, time

__all__ = ['ManyDiscretizationPrm',
           'OneDiscretizationPrm',
           ]

log = log10
inv_log = lambda x: 10**x

# The classes in this module have only static methods, i.e.,
# they are merely name spaces for related functions.

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
        Evaluate the theoretical error model:
        e = error_model(p, d)
        p    : sequence of parameters (to be estimated)
        d    : sequence of (known) discretization parameters
        e    : error
        len(p) must be 2*len(d) in this model
        """
        if len(p) != 2*len(d):
            raise ValueError('len(p)=%d != 2*len(d)=%d' % (len(p),2*len(d)))
        sum = 0
        for i in range(len(d)):
            sum += p[2*i] * d[i]**p[2*i+1]
        return sum

    def nonlinear_fit(d, e, initial_guess):
        """
        @param d: list of values of the set of discretization
              parameters in each experiment:
              d = ((d_1,d_2,d_3),(d_1,d_2,d_3,),...);
              d[i] provides the values of the discretization
              parameters in experiement no. i.
        @param e: list of error values; e = (e_1, e_2, ...):
              e[i] is the error associated with the parameters
              d[i].
        @param initial_guess: the starting value for the unknown
        parameters vector.
        @return: list of fitted paramters.
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
        sol = leastSquaresFit(ManyDiscretizationPrm.error_model,
                              initial_guess, data)
        # return list of fitted parameters (p in error_model)
        # (sol[1] is a measure of the quality of the fit)
        return sol[0]  

    error_model = staticmethod(error_model)
    nonlinear_fit = staticmethod(nonlinear_fit)

class OneDiscretizationPrm(object):
    """
    Tools for fitting an error model with only one discretization
    parameter: e = C*h^2.
    """
    
    def error_model(p, d):
        """e = C*h**a"""
        C, a = p
        h = d[0]
        return C*h**a

    def loglog_error_model(p, d):
        """Requires log-log data."""
        C, a = p
        h = d[0]
        return log(C) + a*log(h)


    def linear_loglog_fit(d, e):
        """
        Linear least squares algorithm.
        Suitable for problems with only one distinct
        discretization parameter.

        d  : sequence of discretization parameter values
        e  : sequence of corresponding error values

        The error model the data is supposed to fit reads
        log(e[i]) = log(C[i]) + a*log(d[i])
        """
        A = transpose(array([d, zeros(len(d), Float)+1]))
        sol = LinearAlgebra.lstsq(A, e)
        a, logC = sol[0]
        C = inv_log(logC)
        return a, C

    def nonlinear_fit(d, e, initial_guess):
        """
        @param d: list of values of the (single) discretization
              parameter in each experiment:
              d[i] provides the values of the discretization,
              parameter in experiement no. i.
        @param e: list of error values; e = (e_1, e_2, ...),
              e[i] is the error associated with the parameters
              d[i]

        @param initial_guess: the starting value for the unknown
        parameters vector.
        @return: a, C; a is the exponent, C is the factor in front.
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
        sol = leastSquaresFit(OneDiscretizationPrm.error_model,
                              initial_guess, data)
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
        Plot results.
        """
        # convert to NumPy arrays:
        d = array(d, Float);  e = array(e, Float)

        # linear least squares fit:
        a, C = OneDiscretizationPrm.linear_loglog_fit(log(d), log(e))
        print "linear LS fit: const=%e rate=%.1f" % (C, a)

        # nonlinear least squares fit (no log-log):
        a2, C2 = OneDiscretizationPrm.nonlinear_fit(d, e, initial_guess)
        print "nonlinear LS fit: const=%e rate=%.1f" % (C2, a2)

        # pairwise estimate of the rate:
        rates, C3 = OneDiscretizationPrm.pairwise_rates(d, e)
        a3 = rates[-1]
        print "pairwise fit: const=%e rate=%.1f" % (C3, a3)
        print "all rates:", rates
        # Note that one_discrprm... returns a, C while the other
        # function returns C, a. The linear least squares fit is fixed,
        # and the other has the parameter sequence defined in the
        # error model.

        # C*h^r plot:
        if 0:
            g1 = Gnuplot.Gnuplot(persist=1)
            g1('set key left box')
            g1('set pointsize 2')
            g1('set title "%s"' % plot_title)
            data = Gnuplot.Data(d, e,
                                **{'with': 'points', 'title': 'data'})
            fit1 = Gnuplot.Func('%(C)g*x**%(a)g' % vars(),
                                **{'with': 'lines',
                                   'title': 'linear log-log least-squares fit'})
            fit2 = Gnuplot.Func('%(C2)g*x**%(a2)g' % vars(),
                                **{'with': 'lines',
                   'title': 'nonlinear direct least-squares fit'})
            fit3 = Gnuplot.Func('%(C3)g*x**%(a3)g' % vars(),
                                **{'with': 'lines',
                   'title': 'successive rates; two last experiments'})
            g1.plot(data, fit1, fit2, fit3)
            time.sleep(2)

        # log-log plot:
        g2 = Gnuplot.Gnuplot(persist=1)
        g2('set key left box')
        g2('set pointsize 2')
        g2('set title "%s"' % plot_title)
        data = Gnuplot.Data(log(d), log(e),
                            **{'with': 'points', 'title': 'data'})
        curves = [data]
        fit1 = Gnuplot.Func('%g + %g*x' % (log(C), a),
                            **{'with': 'lines',
        'title': 'linear log-log least-squares fit: %.1f*h^%.1f' % (C, a)})
        curves.append(fit1)
        if C2 > 0:
            fit2 = Gnuplot.Func('%g + %g*x' % (log(C2), a2),
                                **{'with': 'lines',
            'title': 'nonlinear direct least-squares fit: %.1f*h^%.1f' % \
                                   (C2, a2)})
            curves.append(fit2)
        if C3 > 0:
            fit3 = Gnuplot.Func('%g + %g*x' % (log(C3), a3),
                                **{'with': 'lines',
            'title': 'successive rates; two last experiments: %.1f*h^%.1f' % \
                                   (C3, a3)})
            curves.append(fit3)
        g2.plot(*curves)
        g2.hardcopy(filename=filename, enhanced=1, mode='eps',
                    color=0, fontname='Times-Roman', fontsize=18)
        time.sleep(2)
        

    error_model = staticmethod(error_model)
    loglog_error_model = staticmethod(loglog_error_model)
    linear_loglog_fit = staticmethod(linear_loglog_fit)
    nonlinear_fit = staticmethod(nonlinear_fit)
    pairwise_rates = staticmethod(pairwise_rates)
    analyze = staticmethod(analyze)

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
    and the final r value is used for return.
    """
    rates, C = OneDiscretizationPrm.pairwise_rates(discretization_prm, error)
    # improvement: check that there is no divergence at the end of
    # the series of experiments
    return C, rates[-1]


# no need for this one?
def __many_discrprm_log_fit(d, e, factors):
    """
    Linear least squares algorithm.
    Suitable for problems with a common
    discretization parameter, i.e., a common
    convergence rate for each parameter.
    Only the exponent can be estimated.
    
    @param d: sequence of the main discretization parameter values.
    @param e: sequence of corresponding error values.
    @param factors: multiply factors[j]*d[i][j] such that
    the rate gets the same.

    The error model the data is supposed to fit reads
    log(e[i]) = log(C[i]) + a*log(d[i])
    """
    # not ready, just a copy:
    A = transpose(array([d, zeros(len(d), Float)+1]))
    sol = LinearAlgebra.lstsq(A, e)
    a, logC = sol[0]
    C = inv_log(logC)
    return a, C

"""
Experimental code for analyzing experiments:

Idea: fill a table of (dt,h,error) tuples. Explore the diagonal
and the right column and bottom row for convergence rate,
and the whole table, generalize to more discretization prms.
Assume: matrix table, h/dt**q=f, q and f given, assumed rate p

Along the diagonal: h/dt**q=f, factorize h and use linear least squares
row/column: E = dt-error + C*h^p, use three values, form E_3-E_1, E_3-E_2
to eliminate dt-error, factorize h_1^p, guess p to absorb coeff into C,
linear least squares or two successive values for C and p

Problem with linear least squares: if we are not asymptotic, we get
wrong C and p estimates, two succ experiments are better
Fill in new table with errors replaced by conv rates based on two
successive experiments (this and the last)


def power_seq(start, stop, reduction_factor=2.0):
    values = [start]
    while values[-1] > stop:
        values.append(values[-1]/reduction_factor)

dx = power_seq(0.5,1.0-7)
dt = dx*dx/2.0
resolution = (('dx', dx), ('dt', dt))
experiment = []
for _dx in dx:
    for _dt in dt:
        experiment.append((dx,dt,error))

class TableAnalyzer:
    def __init__(self, resolution, experiment):
        self.resol = resolution
        self.names = [name for name, values in resolution]
        self.data = experiment

    def make_table(self):
        # turn self.data into multi-dimensional table
        import multipleloop
        table, names, varied = multipleloop.combine(self.resol)
"""

        
import random
def _test1():
    """Single discretization parameter test."""
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

# missing tasks:
# example with dx, dy and dt
# same example, but with factors to get a common rate
# dx, dt tables and experiments with whole table, one
# column and one row, and the diagonal

if __name__ == '__main__':
    if len(sys.argv) == 1:
        _test1()
        print 'Usage: %s filename C-guess r-guess' % sys.argv[0]
    else:
        analyze_filedata()
