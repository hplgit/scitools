from scitools.all import *
from time import sleep

x = seq(0, 15, 0.2)
y = sin(x)*x
v = sin(x)*sqrt(x)
w = sin(x)*x**0.33333333

plot(x, y, 'r-', x, v, 'b--', x, w, 'g--',
     legend=('sin(x)*x', 'sin(x)*sqrt(x)', 'sin(x)*x**(1/3)'),
     title='plot demo 5', xlabel='X', ylabel='Y')
sleep(3)

# get backend and fine-tune the plot:
g = get_backend()
print type(g), g  # Gnuplot instance
g('set key left box')
g('set grid')
g('set xlabel "X" font "Helvetica,14"')
g('set ylabel ""')
g.replot()
g('set output "tmp.png"')
g('set term png small')
g.replot()




