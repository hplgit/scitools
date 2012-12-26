#!/usr/bin/env python

"""
Demonstration of some more advanced examples on how to use the surf command
to plot surfaces.
"""

from scitools.std import *

def test():
    """Converted version of the Klein Bottle demo in Matlab."""
    n = 12;
    a = .2;                         # the diameter of the small tube
    c = .6;                         # the diameter of the bulb
    t1 = seq(pi/4, 5*pi/4, pi/n);   # parameter along the tube
    t2 = seq(5*pi/4, 9*pi/4, pi/n); # angle around the tube
    
    u = seq(pi/2, 5*pi/2, pi/n)
    X,Z1 = ndgrid(t1,u,sparse=False)
    Y,Z2 = ndgrid(t2,u,sparse=False)

    setp(interactive=False)
    # The handle
    len_ = sqrt(sin(X)**2 + cos(2*X)**2);
    x1 = c*ones(shape(X))*(cos(X)*sin(X)
                           - 0.5*ones(shape(X))+a*sin(Z1)*sin(X)/len_);
    y1 = a*c*cos(Z1)*ones(shape(X));
    z1 = ones(shape(X))*cos(X) + a*c*sin(Z1)*cos(2*X)/len_;
    #import sys; sys.exit()
    handleHndl=surf(x1,y1,z1,X);
    #set(handleHndl,'EdgeColor',[.5 .5 .5]);
    hold('on');

    # The bulb
    r = sin(Y) * cos(Y) - (a + 1./2) * ones(shape(Y));
    x2 = c * sin(Z2) * r;
    y2 = - c * cos(Z2) * r;
    z2 = ones(shape(Y)) * cos(Y);
    bulbHndl=surf(x2,y2,z2,Y);
    #set(bulbHndl,'EdgeColor',[.5 .5 .5])

    try: colormap(hsv());
    except NotImplementedError: pass
    axis('vis3d')
    view(-37,30);
    axis('off')
    light(lightpos=(2,-4,5))
    light()
    #shading('interp')
    hold('off')
    show()

def test2():
    """Converted version of the Werner Boy's Surface demo in Matlab."""
    n = 128;
    u = linspace(0,pi,n);
    v = linspace(0,pi,n);
    
    u = u[newaxis,:]*ones((n,1))
    v = v[:,newaxis]*ones((1,n))
    #u = repmat(u,n,1);
    #v = repmat(transpose(v),1,n);

    x = cos(v)*sin(u);
    y = sin(v)*sin(u);
    z = cos(u);
    f = 1./2*((2*x**2-y**2-z**2) + 2*y*z*(y**2-z**2) + 
             z*x*(x**2-z**2) + x*y*(y**2-x**2));
    g = sqrt(3)/2 * ((y**2-z**2) + z*x*(z**2-x**2) + x*y*(y**2-x**2));
    h = (x+y+z)*((x+y+z)**3 + 4*(y-x)*(z-y)*(x-z));

    setp(interactive=False)
    s = surf(f,g,h/10,u,
             shading='interp',
             daspect=[1,1,1],
             view=(-40,32),
             axis='off')
    try: colormap(jet())
    except NotImplementedError: pass 
    #'LineStyle','none', ...
    #'FaceLighting','gouraud', ...
    #'FaceColor','interp');
    
    #l1 = light();
    #l2 = light();
    #lightangle(l1,70,-40);
    #lightangle(l2,-30,80);
    camzoom(1.5)
    show()

def test3():
    """Converted version of the knot demo in Matlab."""
    # Number of grid points in each (circular) section of the tube.
    m = 20;
    # Number of sections along the tube.
    n = 60;
    # Radius of the tube.
    R = 0.75;
    # Symmetry index.  Try q=floor(n/3) (symmetric) or q=floor(n/4)
    q = int(floor(n/3));

    # Do not change this!
    t = seq(0,n)/n;

    # The generating function f0 must be 1-periodic.
    # f1 and f2 are the first and second derivatives of f0.
    a = 2; b = 3; c = 1.5;
    q1=2; q2=4;
    f0 = sin(q1*pi*t) + a*sin(q2*pi*t) - \
         b*cos(4*pi*t)/2 + c*sin(6*pi*t);
    f1 = (q1*pi)*cos(q1*pi*t) + a*(q2*pi)*cos(q2*pi*t) + \
         b*(4*pi)*sin(4*pi*t)/2 + c*(6*pi)*cos(6*pi*t);
    f2 = -(q1*pi)**2*sin(q1*pi*t) - a*(q2*pi)**2*sin(q2*pi*t) + \
         b*(4*pi)**2*cos(4*pi*t)/2 - c*(6*pi)**2*sin(6*pi*t);

    # Extend f periodically to 2 period-intervals:
    #f0 = [ f0(1:n) f0(1:n) ];
    f0 = ravel(array([f0[0:n],f0[0:n]], float))
    #f1 = [ f1(1:n) f1(1:n) ];
    f1 = ravel(array([f1[0:n],f1[0:n]], float))
    #f2 = [ f2(1:n) f2(1:n) ];
    f2 = ravel(array([f2[0:n],f2[0:n]], float))

    # [x10;x20;x30] is the parametric representation of
    # the center-line of the tube:
    x10 = f0[0:n+1] #f0(1:n+1);
    x20 = f0[q:q+n+1];
    x30 = f0[2*q:2*q+n+1];

    # [x11;x21;x51] is velocity (same as tangent) vector:
    x11 = f1[0:n+1];
    x21 = f1[q:q+n+1];
    x51 = f1[2*q:2*q+n+1];

    # [x12;x22;x32] is acceleration vector:
    x12 = f2[0:n+1];
    x22 = f2[q:q+n+1];
    x32 = f2[2*q:2*q+n+1];

    speed = sqrt(x11**2 + x21**2 + x51**2);

    # This is the dot-product of the velocity and acceleration vectors:
    velacc = x11*x12 + x21*x22 + x51*x32;

    # Here is the normal vector:
    nrml1 = speed**2 * x12 - velacc*x11;
    nrml2 = speed**2 * x22 - velacc*x21;
    nrml3 = speed**2 * x32 - velacc*x51;
    normallength = sqrt(nrml1**2 + nrml2**2 + nrml3**2);

    # And here is the normalized normal vector:
    unitnormal1 = nrml1 / normallength;
    unitnormal2 = nrml2 / normallength;
    unitnormal3 = nrml3 / normallength;

    # And the binormal vector ( B = T x N )
    binormal1 = (x21*unitnormal3 - x51*unitnormal2) / speed;
    binormal2 = (x51*unitnormal1 - x11*unitnormal3) / speed;
    binormal3 = (x11*unitnormal2 - x21*unitnormal1) / speed;

    # s is the coordinate along the circular cross-sections of the tube:
    s = seq(0,m)[:,newaxis];
    s = (2*pi/m)*s;

    # Each of x1, x2, x3 is an (m+1)x(n+1) matrix.
    # Rows represent coordinates along the tube.  Columns represent coordinates
    # in each (circular) cross-section of the tube.

    xa1 = ones((m+1,1))*x10;
    xb1 = (cos(s)*unitnormal1 + sin(s)*binormal1);
    xa2 = ones((m+1,1))*x20;
    xb2 = (cos(s)*unitnormal2 + sin(s)*binormal2);
    xa3 = ones((m+1,1))*x30;
    xb3 = (cos(s)*unitnormal3 + sin(s)*binormal3);
    color = ones((m+1,1))*(seq(0,n)*2/n-1);

    x1 = xa1 + R*xb1;
    x2 = xa2 + R*xb2;
    x3 = xa3 + R*xb3;

    setp(interactive=False)
    surf(x1,x2,x3,color);
    shading('interp');
    light()
    #lighting gouraud % 'lighting phong' will use zbuffer, slower
    view(2)
    axis('equal')
    axis('off')
    axis('vis3d') # for smooth rotate3d
    show()

if __name__ == '__main__':
    test()
    figure()
    test2()
    figure()
    test3()
    raw_input('Press Return key to quit: ')
