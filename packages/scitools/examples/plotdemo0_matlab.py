from scitools.all import *

# plot two curves in the same plot:
x = seq(0, 15, 0.2)   # 0, 0.2, 0.4, ...., 15
y1 = sin(x)*x
y2 = sin(x)*sqrt(x)

# use Matlab syntax:
plot(x, y1, 'b-')
hold('on')
plot(x, y2, 'ro')
legend('x*sin(x)', 'sqrt(x)*sin(x)')
title('Simple Plot Demo')
axis([0, 15, -25, 25])
xlabel('X')
ylabel('Y')
show()

hardcopy('tmp1.ps')  # this one can be included in latex
hardcopy('tmp1.png') # this one can be included in HTML



