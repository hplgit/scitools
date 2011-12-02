"""
Exemplify how a vector can be rotated in the plane.
Method: display one vector as a vector field, using quiver,
with a 1x1 cells in the grid and vanishing vectors except
at the first grid point (origin).
The example show how the quiver function can be used to
display single vectors in a coordinate system.
"""
from scitools.std import *

vec1 = matrix([1, 2], dtype=float).transpose()
theta = pi/3  # rotation angle
transformation = matrix([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
print transformation
vec2 = transformation*vec1

# Use quiver to plot vector fields on a 1x1 grid with the field
# being 0 at all points except the origin.

def vec2vecfield(vec, shape):
    """
    Given a vector and the shape (M,N) of an MxN grid,
    return a 2D vector field which is (0,0) at all points
    except for the origin where the field equals vec.
    """
    u, v = zeros(shape), zeros(shape)  # vector field
    u[0,0] = vec[0]; v[0,0] = vec[1]
    return u, v

# Make 1x1 grid
axis_extent_x = 2
axis_extent_y = 2
x = linspace(0, axis_extent_x, 2)  # no of cells: 1x1
y = linspace(0, axis_extent_y, 2)  # no of cells: 1x1
xv, yv = ndgrid(x, y, sparse=False)

u1, v1 = vec2vecfield(vec1, xv.shape)
quiver(xv, yv, u1, v1, 'b')  # b for blue vector
hold('on')
u2, v2 = vec2vecfield(vec2, xv.shape)
quiver(xv, yv, u2, v2, 'r')  # r for red vector
