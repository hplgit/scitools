from scitools.std import *

# Plot a circle
t = linspace(0, 2*pi, 31)
x = cos(t)
y = sin(t)
# Preserve 1-1 aspect mode: set axis and daspectmode
# as part of plot command
plot(x, y, axis=[-1,1,-1,1], daspectmode='equal')

# Plot a hill
figure()
R = 50
tx = linspace(-150, 0, 151)
ty = linspace(0, 150, 151)
x, y = ndgrid(tx, ty)
p0 = 1000
dp = 40
p = p0 - dp/(1 + (x**2 + y**2)/R**2)
surf(x, y, p, colorbar='on')

raw_input('Press Return key to quit: ')
