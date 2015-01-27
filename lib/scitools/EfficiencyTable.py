"""
This module contains a class for managing efficiency/performance
experiments.
"""


class EfficiencyTable:
    """
    Manage the CPU times of efficiency experiments and make
    tabular reports with sorted results.

    >>> e = EfficiencyTable('some description of the experiments')
    >>> e.add('about an experiment', cpu_time)
    >>> e.add('about another experiment', cpu_time)
    >>> e.add('about a third experiment', cpu_time)
    >>> print e  # prints a sorted table with scaled CPU times
    >>> e += e2  # add experiments from EfficiencyTable e2 to e
    """
    def __init__(self, description, normalization_time=None):
        """
        @param description: a string acting as headline for this test.
        @param normalization_time: all CPU times will be divided by this value
        (if not set, the class will find the smallest (best) CPU
        time and divide all others by this value.

        The best_time parameter can also be set in the
        set_normalization_time method. The normalization time is not
        used before an instance is printed (str method).)
        """
        self.description = description
        self.experiments = {}  # key=description, value=[CPU-time1, CPU-time2, ]
        self._normalization_time = normalization_time

    def add(self, description, CPU_time, function_name=None):
        """
        Add the CPU time of an experiment, together with a description
        and an optional function_name (which is appended to the
        description string).
        """
        if function_name is not None:
            # include name of the tested function as part of the description:
            description = description + ' (%s)' % function_name
        if not description in self.experiments:
            self.experiments[description] = []
        self.experiments[description].append(CPU_time)

    def __iadd__(self, other):
        """
        Add results in other to present results.
        New items (descriptions) are simply registered, while
        identical items (descriptions) will have a list of CPU times,
        corresponding to the different EfficiencyTable instances.
        """
        self.description += '\n' + other.description
        for e in other.experiments:
            if e in self.experiments:
                # this experiment is already registered, add the lists of CPU times:
                self.experiments[e].extend(other.experiments[e])
            else:
                self.experiments[e] = other.experiments[e]
        return self

    def __add__(self, other):
        """As e += table (see __iadd__)."""
        e = EfficiencyTable(self.description)
        e.experiments = self.experiments.copy()
        e.__iadd__(other)
        return e

    def set_normalization_time(self, t):
        """
        Set the CPU time by which all other CPU times will be divided.
        By default, this is the maximum CPU time encountered in the data.
        """
        self._normalization_time = t

    def _reference_CPU_time(self, experiment_idx=0):
        if self._normalization_time is not None:
            # try first to see if there is an experiment with the
            # given normalization time, and if so, use the corresponding
            # description, otherwise use a dummy description:
            for description in self.experiments:
                if abs(self.experiments[description][experiment_idx] - \
                       self._normalization_time) < 1.0E-10:
                    return self._normalization_time, description
            # no experiment coincides with the given normalization time
            description = 'some external experiment'
            self.experiments[description] = [self._normalization_time]
            return self._normalization_time, description


        # no given normalization time, find best performance:
        # (only search among positive CPU times for an experiment with
        # index experiment_idx)
        best = 1.0E+20
        cpu_eps = 1.0E-9  # smallest reliable CPU time (but many repetitions
                          # may produce small time per call while the
                          # measurements are reliable)
        for description in self.experiments:
            cpu_time = self.experiments[description][experiment_idx]
            # drop counting very small (unreliable) or negative
            # (erroneous timings) CPU times:
            if cpu_time > cpu_eps:
                if cpu_time < best:
                    best = cpu_time
                    best_key = description

        if best == 1.0E+20:
            # did not find any CPU time > cpu_eps
            raise ValueError('too small CPU times (all less than %E)' % cpu_eps)
        return best, best_key

    def __str__(self):
        """
        Print out a sorted list (with respect to CPU times) of the experiments.
        In case of multiple CPU times per description of an experiment,
        the table is sorted with respect to the first CPU time entry of each
        multiple CPU times list. All CPU times are divided by a normalization
        time, which is given to the constructor or to the
        set_normalization_time method, or if not prescribed, this class
        finds the smallest reliable CPU time (neglecting very small
        CPU time).
        """
        # inv_dict is the inverse dictionary of self.experiments, i.e.,
        # CPU time is the key and the description is the valid.
        # Only the first CPU time entry is used.

        # inv_dict computation does not work if the CPU times are very
        # small (0.00 is the key of many), so we need to add a small
        # random number to very small CPU times
        import random, math
        inv_dict = {}  # inverse of self.experiments
        for k in self.experiments:
            CPU_time = self.experiments[k][0]
            if math.fabs(CPU_time) < 1.0E-7:
                CPU_time += 1.0E-14*random.random()
            if CPU_time in inv_dict:
                # this destroys the one-to-one mapping, perturb CPU_time:
                CPU_time *= 1.0 + 1.0E-3*random.random()
            self.experiments[k][0] = CPU_time
            inv_dict[CPU_time] = k
        # sort CPU-times:
        cpu_times0 = list(inv_dict.keys())
        cpu_times0.sort()
        s = '\n\n' + '*'*80 + '\n' + self.description + '\n' + '*'*80 + '\n'
        self.best, self.best_key = self._reference_CPU_time(0)
        s += 'reference CPU time based on the experiment\n   "%s"\nwith '\
             'CPU time:\n  %s\n\n' % \
             (self.best_key, str(self.experiments[self.best_key])[1:-1])

        max_length = max([len(string) for string in
                          list(self.experiments.keys())])
        for cpu_time_key in cpu_times0:
            description = inv_dict[cpu_time_key]
            s += '%%-%ds | ' % max_length % description
            for cpu_time, ref_time in \
                    zip(self.experiments[description],
                        self.experiments[self.best_key]):
                nc = cpu_time/ref_time
                if abs(nc) > 9999.0:
                    s += '%10.1e' % nc
                else:
                    s += '%8.2f' % nc
            s += '\n'
        return s

def plot(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):
        if lines[i].find('CPU times') >= 0:
            start = i+3
            break
    counter = 1
    curves = {}
    labels = open('tmp_plot_labels', 'w')
    import math
    for line in lines[start:]:
        name, numbers = line.split('|')
        curves[name] = [float(x) for x in numbers.split()]
        for i in range(len(curves[name])):
            try:
                curves[name][i] = math.log10(curves[name][i])
            except ValueError:
                curves[name][i] = 0.0
        f = open('tmp_plot_%02d' % counter, 'w')
        for i in range(len(curves[name])):
            v = curves[name][i]
            if v > 0.0:
                f.write('%2d  %g\n' % (i+1, v))
        f.close()
        counter += 1
        labels.write('%2d: %s\n' % (counter, name))
    labels.close()
    # generate Gnuplot script:
    plotfiles = ['"tmp_plot_%02d" title "%d" with lines' % (i,i) \
                 for i in range(1,len(lines[start:])+1)]
    cmd = 'plot ' + ', '.join(plotfiles)
    f = open('tmp_plot.gnuplot', 'w')
    f.write("""
set xrange [0:%d]
%s
""" % (len(curves[name])+1, cmd))
    f.close()



def _test(n):
    # how much does it cost to run an empty loop with
    # range, xrange and iseq?
    e = EfficiencyTable('Empty loops, loop length = %d' % n)
    import timeit
    t1 = timeit.Timer('for i in range(n): pass',
                      setup='n=%d' % n).timeit(5)
    e.add('for i in range(n): pass', t1)
    t2 = timeit.Timer('for i in xrange(n): pass',
                      setup='n=%d' % n).timeit(5)
    e.add('for i in xrange(n): pass', t2)
    t3 = timeit.Timer('for i in iseq(stop=n-1): pass',
                      setup='from scitools.numpyutils import iseq;' +
                      'n=%d' % n).timeit(5)
    e.add('for i in iseq(stop=n-1): pass', t3)
    print e

if __name__ == '__main__':
    import sys
    try:
        n = int(sys.argv[1])
    except:
        n = 100
    _test(n)
