#!/usr/bin/env python

"""
Demonstration on how to deal with greek letters and mathematics
in axis labels, titles, legends, and text.
"""
from scitools.std import *

def do_plot(latex='no'):
    tau_1 = linspace(0, 3, 151)
    tau_2 = linspace(0, 3, 11)
    alpha = 1
    theta_1 = tau_1*exp(-alpha*tau_1**2)
    theta_2 = sqrt(tau_2)*exp(-alpha*tau_2**2)
    if latex == 'with $':
        # standard latex text in legends, labels, and title
        plot(tau_1, theta_1, 'r-',
             tau_2, theta_2, 'bo',
             legend=(r'$\theta_1 = \tau e^{-\alpha\tau^2}$',
                     r'$\theta_2 = \sqrt{\tau} e^{-\alpha\tau^2}$'),
             title=r'Plot of $\theta_1$ and $\theta_2$, $\alpha = \sum_{i=1}^n \phi_i$' + ' (%s) ' % latex.replace('$', 'dollar'),
             xlabel=r'$\tau$',
             ylabel=r'$\theta$',
             savefig='tmp_' + backend + '_' + latex.replace(' $', '_dollar') + '.eps')
    elif latex == 'without $':
        # latex math without dollars - some backends will automatically
        # treat this the right way
        plot(tau_1, theta_1, 'r-',
             tau_2, theta_2, 'bo',
             legend=(r'\theta_1 = \tau e^{-\alpha\tau^2}',
                     r'\theta_2 = \sqrt{\tau} e^{-\alpha\tau^2}'),
             title=r'Plot of \theta_1 and \theta_2, \alpha = \sum_{i=1}^n \phi_i' + ' (%s) ' % latex.replace('$', 'dollar'),
             xlabel=r'\tau',
             ylabel=r'\theta',
             savefig='tmp_' + backend + '_' + latex.replace(' $', '_dollar') + '.eps')
    elif latex == 'no':
        # No latex math, just plain words
        plot(tau_1, theta_1, 'r-',
             tau_2, theta_2, 'bo',
             legend=(r'theta_1 = tau exp(-alpha*tau^2)',
                     r'theta_2 = sqrt(tau)*exp(-\alpha*tau^2)'),
             title='Plot of theta_1 and theta_2, alpha = sum_i phi_i' + ' (%s) ' % latex.replace('$', 'dollar'),
             xlabel=r'tau',
             ylabel=r'theta',
             savefig='tmp_' + backend + '_' + latex + '.eps')

print backend
for latex in 'no', 'with $', 'without $':
    figure()
    print 'latex: %s' % latex
    do_plot(latex)
raw_input('Press Return: ')

"""
Summary:

=== gnuplot ===

Plain text (no latex, no dollars) works best. Output in .eps file
will recognize sub and super scripts, and also many greek letters if
the letters are written in latex syntax with an opening backslash.
For .eps hardcopies a little tweaking with inserting some
backslashes if often desirable.

Lables like \tau and \theta get typeset as tab "au" and tab "heta"
due to file communication between python and gnuplot (just skip
the backslashes to avoid this, raw strings do not help - then the
backslash survives).

=== matplotlib ===

Labels and legends work well with and without dollars. The title
should be plain text with embedded dollars and latex as needed.
Real latex text is what is recommended for matplotlib.

"""
