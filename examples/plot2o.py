from scitools.std import *
n = 20  # no of periods of a sine function
r = 80  # resolution of each period
x = linspace(0, n, r*n + 1)
amplitude = 1 + sin(2*pi*0.05*x)
y = amplitude*sin(2*pi*x)

r = (y.max() - y.min())/x[-1]
print 'ratio:', r

subplot(2, 1, 1)
plot(x, y,
     axis=[x[0], x[-1], y.min(), y.max()],
     daspectmode='equal',
     title='daspectmode=equal',
     )
subplot(2, 1, 2)
plot(x, y,
     axis=[x[0], x[-1], y.min(), y.max()],
     daspect=[0.5,1,1],
     daspectmode='manual',
     title='daspectmode=manual, daspect=[0.5,1,1]',
     )

figure()
plot(x, y,
     axis=[x[0], x[-1], y.min(), y.max()],
     daspect=[1,1,1],
     daspectmode='manual',
     title='daspectmode=manual, daspect=[1,1,1]',
     )

show()
raw_input()
