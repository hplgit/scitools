#!/usr/bin/env python

from scitools.easyviz import *
from Numeric import array, sin, cos, sqrt, pi, ones, zeros, Float
from scipy import linspace
import time

"""
xsub = x(1:10,20:30,1:7);
ysub = y(1:10,20:30,1:7);
zsub = z(1:10,20:30,1:7);
usub = u(1:10,20:30,1:7);
vsub = v(1:10,20:30,1:7);
wsub = w(1:10,20:30,1:7);

lims = [100.64 116.67 17.25 28.75 -0.02 6.86];
[xsub,ysub,zsub,usub,vsub,wsub] = subvolume(x,y,z,u,v,w,lims);
"""

"""
load wind
zmax = max(z(:));
zmin = min(z(:));
streamslice(x,y,z,u,v,w,[],[],(zmax-zmin)/2)
"""

## def test_plot3():
##     nmeridian  = 6; nlongitude = 11;
##     phi = seq(0,2*pi,pi/1000)
##     mu = phi * nmeridian
##     x = cos(mu) .* (1 + cos(nlongitude*mu/nmeridian) / 2.0)
##     y = sin(mu) .* (1 + cos(nlongitude*mu/nmeridian) / 2.0)
##     z = sin(nlongitude*mu/nmeridian) / 2.0
##     plot3(x,y,z)

def test_legend():
    x=seq(-2,2,.2)
    colors = 'r g b c m y k'.split()
    hold('on')
    for i in range(len(colors)):
        plot(x,x**i,'%s'%colors[i],legend='x^%d'%i)
    raw_input('press enter')

def test_subplot2():
    t = seq(0,2*pi,pi/20)
    x,y = meshgrid(t,t)
    subplot(2,2,1)
    plot(sin(t),cos(t),axis='equal') 

##     subplot(2,2,2)
##     z = sin(x)+cos(y)
##     plot(t,z)
##     axis([0, 2*pi, -2, 2])

##     subplot(2,2,3)
##     z = sin(x)*cos(y)
##     plot(t,z)
##     axis([0, 2*pi, -1, 1])

##     subplot(2,2,4)
##     z = (sin(x)**2)-(cos(y)**2);
##     plot(t,z)
##     axis([0, 2*pi, -1, 1])
    raw_input('press enter')

def test_subplot():
    subplot(2,2,1)
    #xx,yy,zz = meshgrid(seq(-2,2,.2), seq(-2,2,.25), seq(-2,2,.16))
    x = seq(-2,2,.2)
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    slice_(xx, yy, zz, vv, [-1.2,.8,2], 2, [-2,-.2], shading='interp',
           colormap=jet(),
           #xmin=-1,xmax=1,ymin=-1,ymax=1,zmin=-1,zmax=1,
           title='slices',
           #daspect=[1,1,1.5],
           )
    #raw_input('press enter')

    subplot(2,2,2)
    x=linspace(0,3,80); y=sin(2*pi*x); theta=2*pi*x+pi/2;
    quiver(x,y,sin(theta)/10,cos(theta)/10,0.04,'b')
    hold('on'); plot(x,y,'r'); hold('off')
    #raw_input('press enter')

    subplot(2,2,3)
    x = seq(-8,8,.2)
    xx,yy = meshgrid(x,x)
    r = sqrt(xx**2+yy**2) + 0.01
    zz = sin(r)/r
    surfc(xx,yy,zz,colormap=jet(),colorbar='on',cbtitle='test',
          zmin=-0.5,zmax=1,clevels=10,
          #shading='interp',
          title='r=sqrt(x**2+y**2)+eps\nsin(r)/r',
          light=Light(position=(-10,-10,5)),
          )
    #raw_input('press enter')

    subplot(2,2,4)
    #clf()
    x = seq(-2,2,.2)
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    isosurface(xx,yy,zz,vv,0.001,colormap=hsv(),shading='interp',
               title='isosurface')
    hold('on')
    isosurface(xx,yy,zz,vv,-0.1,shading='interp',
               bgcolor=(0,0,0), fgcolor=(1,1,1),
               #axis='tight',
               box='on')
    raw_input('press enter')
##     hardcopy(filename=r'tmp_easyviz_subplot.ps', color=True,
##              fontname='Helvetica', fontsize=18)

def test_plot():
    x = seq(-2,2,.1)
    colors = 'r b g c m y k w'.split()
    for i,c in zip(range(1,5),colors):
        subplot(2,2,i)
        plot(x,x**i,'%s' % c,title='subplot(2,2,%d)' % i)
        raw_input('press enter')
    raw_input('press enter')
    subplot(2,2,1)
    plot(x,x**5,'k',title='subplot(2,2,1)')
    raw_input('press enter')
    clf()
    hold('on')
    i = 1
    axis([-2,2,0,10])
    for color in plt._colors:
        plot(x,x*0+i,color,box='on',title='colors')
        i += 1
    raw_input('press enter')
    clf()
    t = seq(0,2*pi,2*pi/100)
    plot(cos(t),sin(t),title='circle',axis='equal')
    raw_input('press enter')
    t = seq(0,2*pi,pi/20)
    plot(sin(t),2*cos(t),grid='on',axis='equal')
    raw_input('press enter')
##     plot(x,x**2)
##     xx,yy=meshgrid(x,x)
##     zz=xx**2+yy**2
##     #surf(xx,yy,zz,shading='interp')
##     uu,vv = gradient(zz)
##     #quiver(xx,yy,uu,vv,0)
##     #contour3(xx,yy,zz)
##     streamline(xx,yy,uu,vv,x,x**2)
##     raw_input('press enter')
##     plot(x,x*0+3)
##     raw_input('press enter')
##     x=linspace(0,3,80); y=sin(2*pi*x); theta=2*pi*x+pi/2;
##     quiver(x,y,sin(theta)/10,cos(theta)/10,0.04,'b')
##     hold('on'); plot(x,y,'b'); hold('off')
##     raw_input('press enter')


def my_test():
    x = seq(-3,3,.1)
    xx,yy = meshgrid(x,x)
    zz = peaks(xx,yy)

    surfc(xx,yy,zz,zmin=-10,zmax=10,shading='interp',box='on',
          clevels=15,clabels='on',hidden='on')
    raw_input('press enter')
    #surf(xx,yy,zz,zmin=-10,zmax=10,shading='interp',view=(90,90),hidden='on')
    #surf(xx*2,yy*3,zz+2)
    raw_input('press enter')

def test_streamribbon():
    xmin = -7; xmax = 7
    ymin = -7; ymax = 7 
    zmin = -7; zmax = 7 
    x = linspace(xmin,xmax,30)
    y = linspace(ymin,ymax,20)
    z = linspace(zmin,zmax,20)
    x,y,z = meshgrid(x,y,z,sparse=False)
    u = y; v = -x; w = 0*x+1

    set(show=False)
    hold('on')
    daspect([1,1,1])
    #cx,cy,cz = meshgrid(linspace(xmin,xmax,30),linspace(ymin,ymax,30),[-3,4])
    #h2=coneplot(x,y,z,u,v,w,cx,cy,cz, 'q')
    #set(h2, 'color', 'k');
      
    sx,sy,sz = meshgrid([-1,0,1],[-1,0,1],[-6]*3,sparse=False)
    p = streamribbon(x,y,z,u,v,w,sx,sy,sz,view=3,shading='interp')
    sx,sy,sz = meshgrid(seq(1,6),zeros(6,Float),[-6]*6,sparse=False)
    p2 = streamribbon(x,y,z,u,v,w,sx,sy,sz,camproj='perspective')
      
    view(-30,10); axis('off'); axis('tight')
    #camproj(p);
    camva(66); camlookat(); camdolly(0,0,.5)#,'f')
    #camlight()
    set(show=True)
    show()
    raw_input('press enter')

def test_streamtube():
    x = seq(-2,2,1)
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    px,py,pz = gradient(vv)
    streamtube(xx,yy,zz,px,py,pz,[0.1]*5,[-.5,-.2,0,.1,.5],seq(-2,2,1),
               #zmin=-.2,zmax=.2,
               daspect=[1,1,1],
               )
    raw_input('press enter')

def test_streamline():
    x = seq(-2,2,.2)
    xx,yy = meshgrid(x,x)
    zz = xx*exp(-xx**2-yy**2)
    px,py = gradient(zz)
    streamline(xx,yy,px,py,[.2,-.2],[-.5,-.5],.2,title='streamlines',hold='on')
    quiver(xx,yy,px,py,4)
    #contour(xx,yy,zz,10)
    raw_input('press enter')
    hold('off')
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    px,py,pz = gradient(vv)
    streamline(xx,yy,zz,px,py,pz,x,x,x)
    raw_input('press enter')

def test_slice_():
    #xx,yy,zz = meshgrid(seq(-2,2,.2), seq(-2,2,.25), seq(-2,2,.16))
    x = seq(-2,2,.2)
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    slice_(xx, yy, zz, vv, [-1.2,.8,2], 2, [-2,-.2],
           #shading='interp', colormap=jet(),
           #xmin=-1,xmax=1,ymin=-1,ymax=1,zmin=-1,zmax=1,
           title='slices at x=[-1.2,.8,2], y=2, and z=[-2,-.2]'
           )
    #slice_(xx, yy, zz, vv, 0, 0, 0, shading='faceted')
    raw_input('press enter')
##     cs = contourslice(xx, yy, zz, vv, [-.7,.7], [], [-.1,0,.1], #[-2,-1,0,1,2],
##                       #xmin=-1,xmax=1,ymin=-2,ymax=0,daspect=[1,1,1],
##                       #zmin=-.1,zmax=.1,
##                       linewidth=3,
##                       )
##     raw_input('press enter')
##     sx,sy = meshgrid(x,x)
##     sz = sy #peaks(sx,sy)
##     slice_(xx,yy,zz,vv,sx,sy,sz,grid='on')
##     raw_input('press enter')

def test_slice_2():
    x = seq(-2,2,.1)
    #xx,yy,zz = meshgrid(x,x,x)
    xx,yy,zz = meshgrid(seq(.1,10,.2),seq(-3,3,.25),seq(-3,3,.25))
    #xv,yv,zv,vv = flow(xx,yy,zz)
    xx,yy,zz,vv = flow(xx,yy,zz)

    xmin = min(ravel(xx))
    ymin = min(ravel(yy)) 
    zmin = min(ravel(zz))

    xmax = max(ravel(xx)) 
    ymax = max(ravel(yy)) 
    zmax = max(ravel(zz))

    set(show=False)

    hslice = surf(linspace(xmin,xmax,100),
                  linspace(ymin,ymax,100),
                  zeros((100,100)))
    #clf()

    #rotate(hslice,[-1,0,0],-45)
    xd = hslice.get('xdata')
    yd = hslice.get('ydata')
    zd = hslice.get('zdata')
    #delete(hslice)

    h = slice_(xx,yy,zz,vv,[],[],0)#xd,yd,zd)
    #h = slice_(xx,yy,zz,vv,[],[],0)
    h.set(diffuse=.8)
##     h.set('FaceColor','interp',
##           'EdgeColor','none',
##           'DiffuseStrength',.8)

    hold('on')
    hx = slice_(xx,yy,zz,vv,xmax-0.001,[],[])
    #set(hx,'FaceColor','interp','EdgeColor','none')

    hy = slice_(xx,yy,zz,vv,[],ymax,[])
    #set(hy,'FaceColor','interp','EdgeColor','none')

    hz = slice_(xx,yy,zz,vv,[],[],zmin+0.001);
    #set(hz,'FaceColor','interp','EdgeColor','none')

    shading('interp')
    daspect([1,1,1])
    box('on')
    view(-38.5,16)
    #camzoom(1.4)
    camproj('perspective')
    set(show=True)
    show()
    raw_input('press enter')


def test_isosurface():
    x = seq(-2,2,.1)
    #xx,yy,zz = meshgrid(x,x,x)
    xx,yy,zz = meshgrid(seq(.1,10,.2),seq(-3,3,.25),seq(-3,3,.25))
    #xv,yv,zv,vv = flow(xx,yy,zz)
    xx,yy,zz,vv = flow(xx,yy,zz)

    #hpatch = patch(isosurface(xx,yy,zz,vv,0));
    hpatch = isosurface(xx,yy,zz,vv,0,
                        daspect=[1,4,4],
                        view=[-65,20],
                        axis='tight',
                        shading='interp')
    #isonormals(x,y,z,v,hpatch)
    #set(hpatch,'FaceColor','red','EdgeColor','none')
    
    #camlight left; 
    #set(gcf,'Renderer','zbuffer'); lighting phong
    raw_input('press enter')

def test2():
    x = seq(-8,8,.2)
    xx,yy = meshgrid(x,x)
    r = sqrt(xx**2+yy**2) + 0.01
    zz = sin(r)/r
    l = Light(lightpos=(-10,-10,5), lightcolor=(1,1,1))
    surfc(xx,yy,zz,shading='interp',colormap=jet(),
          zmin=-0.5,zmax=1,clevels=10,
          title='r=sqrt(x**2+y**2)+eps\nsin(r)/r',
          light=l,
          legend='sin',
          )
    raw_input('press enter')

def test3():
    x=seq(-3,3,.1)
    X,Y=meshgrid(x,x)
    Z=peaks(X,Y)
    U=X+1; V=Y+1; W=Z+1

    #quiver(X,Y,U*0+.9,V*0+.4)
    #quiver(X,Y,U,V)
##     print seq(len(X.flat)-1).shape
    #quiver(seq(len(X.flat)-1),Y,U,V)
    #raw_input('press enter')
    
##     mesh(X,Y,Z)
##     hold('on')
##     surf(Z,view=(0,0),cvector=[-0.5, -0.2, 0.2, 0.5],
##          colormap=flag(),shading='faceted',colorbar='on',
##          xmin=-2,xmax=2)
    #hold('on')
##     surfc(X,Y,exp(-X**2)*exp(-Y**2), clevels=20,
##           colorbar='on', colormap=gray(),
##           title='meshc(x,y,exp(-x**2)*exp(-y**2))',
##           xlabel='x-axis', ylabel='y-axis', zlabel='z-axis',
##           shading='faceted', #view=(0,-50),
##           cblocation='EastOutside')
##     raw_input('press enter')
##     hold('on')
    
##     quiver3(X,Y,Z,U*0+.9,V*0+.4,W*0+.3)
##     raw_input('press enter')
    #figure()
##     hold('on')
    #box('on')
##     surf(X,Y,Z,colormap=red_tones(),colorbar='on',shading='flat')
##     raw_input('press enter')
    #hold('on')
    #colormap(jet())
    #surf(X,Y,Z,colormap=hsv(),colorbar='on',shading='interp',interactive=True)
    #hold('on')
    
    #Z=sin(X*Y)/(X*Y)
    #Z=cos(X)+cos(Y)
##     surfc(X,Y,Z,clevels=15,#box='on',colormap=hot(),colorbar='on',
##           #camproj='perspective',
##           #caxis=[-2, 2],
##           #clabels='on',
##           grid='on',
##           method='normal',
##           title='surface plot with contours',
##           shading='interp',hidden='on',cblocation='EastOutside',
##           #opacity=.8,ambient=1,
##           #specular=.5, specularpower=0,
##           #daspect=[1,1,1],
##           #xmin=-1,xmax=1,#ymin=-1,ymax=1,
##           #zmin=-10, zmax=10,
##           axis='equal',
##           view=3,
##           #xmin=-2.5,xmax=2.5,ymin=-2.5,ymax=2.5,zmin=-10,zmax=10,
##           legend='z=sin(x*y)/(x*y)',
##           )
##     raw_input('press enter')
    contour(X,Y,Z,10,colormap=hsv(),
             clabels='on',
             #xmin=0, xmax=2, ymin=-1, ymax=1,
             #daspect=[2,2,10],
             )
    #print gca().get('daspect')
    raw_input('press enter')
    
    #import time; time.sleep(2)
    #print plt._g.renwin.camera.GetViewTransformMatrix()
##     view(30,40)
##     raw_input('press enter')
##     view(20,50)
##     raw_input('press enter')
##     contour3(Z,10,cntlabels='on')
##     raw_input('press enter')
    #hardcopy(filename='./test_hardcopy_vtk_offscreen.ps')
##     print get_backend().renwin.camera

##     clf()
##     u,v = meshgrid(seq(0.01,pi,pi/20),seq(0,2*pi,pi/20))
##     x = ( 1 - cos(u) ) * cos( u + 2*pi/3 ) * cos( v + 2*pi/3 ) / 2 
##     y = ( 1 - cos(u) ) * cos( u + 2*pi/3 ) * cos( v - 2*pi/3 ) / 2
##     z = cos( u - 2*pi/3 )
##     mesh(x,y,z,axis='equal')
##     raw_input('press enter')

##     clf()
##     phi,theta = meshgrid(seq(0,pi,pi/250),seq(0,2*pi,pi/250))
##     m0 = 4; m1 = 3; m2 = 2; m3 = 3; m4 = 6; m5 = 2; m6 = 6; m7 = 4
##     r = sin(m0*phi)**m1 + cos(m2*phi)**m3 + sin(m4*theta)**m5 + \
##         cos(m6*theta)**m7;
##     x = r * sin(phi) * cos(theta)
##     y = r * cos(phi)
##     z = r * sin(phi) * sin(theta)
##     surf(x,y,z,axis='equal',shading='interp',view=(0,-110))
##     raw_input('press enter')

def test_2Dvector2():
    x = seq(-2,2,.2)
    xx,yy = meshgrid(x,x,sparse=False)
    zz = xx*exp(-xx**2-yy**2)

##    plot(x,x**2,'ko')
##     plot(x,x**2,'y-',x,x**2,'go')

##     quiver(xx,yy,sin(2*pi*xx/10),sin(2*pi*yy/10),5)

##     x=linspace(0,3,80); y=sin(2*pi*x); theta=2*pi*x+pi/2;
##     quiver(x,y,sin(theta)/10,cos(theta)/10,0.04,'b')
##     hold('on'); plot(x,y,'b3'); hold('off')
##     raw_input('press enter')
    
##     px,py = gradient(zz)
##     contour(xx,yy,zz,10)
##     hold('on')
##     quiver(xx,yy,px,py,0,'b',linewidth=3.0,xmin=-1,xmax=1,)
##     raw_input('press enter')

##     hold('off')
##     x = seq(-2,2,.2)
##     y = seq(-1,1,.2)
##     xx, yy = meshgrid(x,y)
##     zz = xx*exp(-xx**2-yy**2)
##     px, py = gradient(zz,.2,.2)
##     quiver(xx,yy,px,py,5)
##     raw_input('press enter')

##     xx,yy = meshgrid(x,x)
##     zz = peaks(xx,yy)
##     contour(xx,yy,zz,10,hold='off')#,xmin=0.5,xmax=2,ymin=-1,ymax=0.5)
##     uu,vv = gradient(zz,.2)
##     quiver(xx,yy,uu,vv,hold='on')
##     raw_input('press enter')

    # examples taken from:
    # http://www.math.uic.edu/~math210/newlabs/lab7/lab7.html
    
##     xx,yy = meshgrid(seq(-1,1,.1),seq(-1,1,1))
##     quiver(xx,yy,-yy,xx,10)

##     zz = (xx**2+yy**2)/2
##     uu,vv = gradient(zz,.2)
##     quiver(xx,yy,uu,vv)

##     quiver(xx,yy,2*xx,0*yy)

    quiver(.9*xx**2-1,2*yy)

##     quiver(xx,yy,1/(1+yy**2),xx*yy/(1+yy**2)**2)

##     x = seq(-5,5,.3)
##     xx,yy = meshgrid(x,x)
##     quiver(sin(yy),cos(xx),0,box='on')

##     x = seq(-3,1,.1);  y = seq(-2,2,.2)
##     xx,yy = meshgrid(x,y)
##     quiver(xx,yy,yy**3-x**2+5,yy-xx**3-5,10,'r','filled',
##            xmin=-3.5,xmax=1.5,ymin=-2.5,ymax=2.5,
##            legend='quiver')

##     quiver(xx,yy,-xx/sqrt(xx**2+yy**2),-yy/sqrt(xx**2+yy**2))

##     quiver(xx,yy,yy-xx/2,-xx-yy/2)

##     quiver(xx,yy,yy,xx)

##     xx,yy = meshgrid(seq(-1.5,1.5,.1))
##     quiver(xx,yy,xx**3+yy-1,yy**3-xx)
    
    raw_input('press enter')
    
def test_2Dvector():
    x=seq(-3,3,1)
    X,Y=meshgrid(x,x)
##     Z = peaks(X,Y)
    Z = X* exp(-X**2-Y**2)

    # in Matlab:
    # >> [u,v]=surfnorm(X,Y,exp(-X .* X) .* exp(-Y .* Y))
    u=array([[ 0.0000, -0.0000, -0.0001, 0,  0.0001,  0.0000, -0.0000],
             [ 0.0027, -0.0034, -0.0090, 0,  0.0090,  0.0034, -0.0027],
             [ 0.0542, -0.0675, -0.1750, 0,  0.1750,  0.0675, -0.0542],
             [ 0.1459, -0.1808, -0.4406, 0,  0.4406,  0.1808, -0.1459],
             [ 0.0542, -0.0675, -0.1750, 0,  0.1750,  0.0675, -0.0542],
             [ 0.0027, -0.0034, -0.0090, 0,  0.0090,  0.0034, -0.0027],
             [ 0.0000, -0.0000, -0.0001, 0,  0.0001,  0.0000, -0.0000]])

    v=array([[ 0.0000,  0.0027,  0.0542,  0.1459,  0.0542,  0.0027,  0.0000],
             [-0.0000, -0.0034, -0.0675, -0.1808, -0.0675, -0.0034, -0.0000],
             [-0.0001, -0.0090, -0.1750, -0.4406, -0.1750, -0.0090, -0.0001],
             [      0,       0,       0,       0,       0,       0,       0],
             [ 0.0001,  0.0090,  0.1750,  0.4406,  0.1750,  0.0090,  0.0001],
             [ 0.0000,  0.0034,  0.0675,  0.1808,  0.0675,  0.0034,  0.0000],
             [-0.0000, -0.0027, -0.0542, -0.1459, -0.0542, -0.0027, -0.0000]])

    quiver(X,Y,u,v,legend='quiver 2')
    hold('on')
    contour(X,Y,Z,5)    
    raw_input('press enter')

def test_3Dvector():
    x = seq(-2,2,1)
    X,Y=meshgrid(x,x)
    Z = X*exp(-X**2-Y**2)

    U = array([[0.0125,   -0.0003,   -0.0067,   -0.0003,    0.0125],
               [0.2429,   -0.0066,   -0.1341,   -0.0066,    0.2429],
               [0.5628,   -0.0183,   -0.3453,   -0.0183,    0.5628],
               [0.2429,   -0.0066,   -0.1341,   -0.0066,    0.2429],
               [0.0125,   -0.0003,   -0.0067,   -0.0003,    0.0125]])

    V = array([[ 0.0076,   0.0764,         0,   -0.0764,   -0.0076],
               [ 0.0174,   0.1777,         0,   -0.1777,   -0.0174],
               [      0,        0,         0,         0,         0],
               [-0.0174,  -0.1777,         0,    0.1777,    0.0174],
               [-0.0076,  -0.0764,         0,    0.0764,    0.0076]])

    W = array([[0.9999,    0.9971,    1.0000,    0.9971,    0.9999],
               [0.9699,    0.9841,    0.9910,    0.9841,    0.9699],
               [0.8266,    0.9998,    0.9385,    0.9998,    0.8266],
               [0.9699,    0.9841,    0.9910,    0.9841,    0.9699],
               [0.9999,    0.9971,    1.0000,    0.9971,    0.9999]])

    quiver3(X,Y,Z,U,V,W,view=3,
            #daspect=[1,1,1],
            #view=(0,-50),
            legend='quiver3',
            )
    hold('on')
    surf(X,Y,Z)
    raw_input('press enter')

from Numeric import pi, cos, sqrt, ones, shape, floor, transpose

def matlab_test():
    n = 12;
    a = .2;                         # the diameter of the small tube
    c = .6;                         # the diameter of the bulb
    t1 = seq(pi/4, 5*pi/4, pi/n);   # parameter along the tube
    t2 = seq(5*pi/4, 9*pi/4, pi/n); # angle around the tube
    
    u = seq(pi/2, 5*pi/2, pi/n)
    X,Z1 = meshgrid(t1,u,sparse=False)
    Y,Z2 = meshgrid(t2,u,sparse=False)

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

    colormap(hsv());
    #axis vis3d
    view(-37,30);
    axis('off')
    light(lightpos=(2,-4,5))
    light()
    #shading('interp')
    show()
    hold('off')
    raw_input('press enter')

def matlab_test2():
    n = 128;
    u = linspace(0,pi,n);
    v = linspace(0,pi,n);
    
    u = u[NewAxis,:]*ones((n,1))
    v = v[:,NewAxis]*ones((1,n))
    #u = repmat(u,n,1);
    #v = repmat(transpose(v),1,n);

    x = cos(v)*sin(u);
    y = sin(v)*sin(u);
    z = cos(u);
    f = 1./2*((2*x**2-y**2-z**2) + 2*y*z*(y**2-z**2) + 
             z*x*(x**2-z**2) + x*y*(y**2-x**2));
    g = sqrt(3)/2 * ((y**2-z**2) + z*x*(z**2-x**2) + x*y*(y**2-x**2));
    h = (x+y+z)*((x+y+z)**3 + 4*(y-x)*(z-y)*(x-z));

    clf()
    s = surf(f,g,h/10,u,
             shading='interp',
             daspect=[1,1,1],
             colormap=jet(),
             view=(-40,23),
             axis='off')
    #'LineStyle','none', ...
    #'FaceLighting','gouraud', ...
    #'FaceColor','interp');
    
    #l1 = light();
    #l2 = light();
    #lightangle(l1,70,-40);
    #lightangle(l2,-30,80);
    #camzoom(1.5);
    raw_input('press enter')

def matlab_test3():
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
    f0 = ravel(array([f0[0:n],f0[0:n]], Float))
    #f1 = [ f1(1:n) f1(1:n) ];
    f1 = ravel(array([f1[0:n],f1[0:n]], Float))
    #f2 = [ f2(1:n) f2(1:n) ];
    f2 = ravel(array([f2[0:n],f2[0:n]], Float))

    # [x10;x20;x30] is the parametric representation of
    # the center-line of the tube:
    x10 = f0[0:n+1] #f0(1:n+1);
    x20 = f0[q:q+n+1];
    x30 = f0[2*q:2*q+n+1];

    # [x11;x21;x31] is velocity (same as tangent) vector:
    x11 = f1[0:n+1];
    x21 = f1[q:q+n+1];
    x31 = f1[2*q:2*q+n+1];

    # [x12;x22;x32] is acceleration vector:
    x12 = f2[0:n+1];
    x22 = f2[q:q+n+1];
    x32 = f2[2*q:2*q+n+1];

    speed = sqrt(x11**2 + x21**2 + x31**2);

    # This is the dot-product of the velocity and acceleration vectors:
    velacc = x11*x12 + x21*x22 + x31*x32;

    # Here is the normal vector:
    nrml1 = speed**2 * x12 - velacc*x11;
    nrml2 = speed**2 * x22 - velacc*x21;
    nrml3 = speed**2 * x32 - velacc*x31;
    normallength = sqrt(nrml1**2 + nrml2**2 + nrml3**2);

    # And here is the normalized normal vector:
    unitnormal1 = nrml1 / normallength;
    unitnormal2 = nrml2 / normallength;
    unitnormal3 = nrml3 / normallength;

    # And the binormal vector ( B = T x N )
    binormal1 = (x21*unitnormal3 - x31*unitnormal2) / speed;
    binormal2 = (x31*unitnormal1 - x11*unitnormal3) / speed;
    binormal3 = (x11*unitnormal2 - x21*unitnormal1) / speed;

    # s is the coordinate along the circular cross-sections of the tube:
    s = seq(0,m)[:,NewAxis];
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

    clf()
    surf(x1,x2,x3,color);
    shading('interp');
    light()
    #lighting gouraud % 'lighting phong' will use zbuffer, slower
    view(2)
    #axis equal off
    axis('off')
    show()
    #axis vis3d % for smooth rotate3d
    raw_input('press enter')
    #import time
    #time.sleep(5)

def test_quiver():
    x = seq(-3,3,.2);
    y = seq(-3,3,.2);
    clf()
    xx,yy = meshgrid(x,y);
    zz = peaks(xx,yy);
    hold('on')
    #pcolor(x,y,zz);
    axis([-3, 3, -3, 3]);
    #colormap((jet+white)/2);
    shading('interp')
    px,py = gradient(zz,.2,.2);
    quiver(x,y,px,py,5,'k');
    axis('off')
    hold('off')
    raw_input('press enter')

def test_quiver3():
    # http://www.monolith.uwaterloo.ca/software/matlab/HTML/help/techdoc/creating_plots/chspec24.html
    vz = 10  # Velocity
    a = -32  # Acceleration
    t = seq(0,1,.1)
    z = vz*t + 1./2*a*t**2
    vx = 2
    x = vx*t
    vy = 3
    y = vy*t
    u = gradient(x)
    v = gradient(y)
    w = gradient(z)
    scale = 0
    quiver3(x,y,z,u,v,w,scale,
            view=[70,18],
            grid='on',
            xmin=0,xmax=3.5,ymin=0,ymax=3,zmin=-10,zmax=2)
    raw_input('press enter')
    
    x = seq(-3,3,1)
    xx,yy,zz = meshgrid(x,x,x,sparse=False)
    quiver3(xx,yy,zz,xx,yy,zz,'r',
            view=3,
            axis=[-5,5,-5,5,-5,5],
            daspect=[1,1,1],
            grid='on')
    raw_input('press enter')

def test_figure():
    import pprint
    x=seq(-2,2,.1)
    plot(x**2)
    f1=gcf()
    print pprint.pformat(f1.__dict__['_prop'])
    #print pprint.pformat(plt.__dict__)
    raw_input('press enter')
    figure()
    #subplot(1,2,1)
    plot(x,x**3,'r')
    f2 = gcf()
    print pprint.pformat(f2.__dict__['_prop'])
    print f1.get('axes') == f2.get('axes')
    #print pprint.pformat(plt.__dict__)
    raw_input('press enter')

def test_contourf():
    x = seq(-3,3,.1)
    xx,yy = meshgrid(x,x)
    zz = peaks(xx,yy)
    contourf(zz,10,
             caxis=[-20,20],
             title='Filled Contour Plot Using\ncontourf(zz,10)')
    raw_input('press enter')

def test_lights():
    x=seq(-3,3,.1)
    xx,yy=meshgrid(x,x)
    zz=peaks(xx,yy)
    surf(zz,title='No lights')
    #time.sleep(1); figure()
    raw_input('press enter')
    surf(zz,light=Light(),title='default light')
    #time.sleep(1); figure()
    raw_input('press enter')
    surf(zz,light=Light(lightpos=(-10,-10,10),lightcolor=(.5,.5,.5)),
         title='light at (-10,-10,10) and color (0,0,1)')
    #time.sleep(1); figure()
    raw_input('press enter')
    surf(zz,title='No lights')
    raw_input('press enter')

def test_pcolor():
    n = 6;
    r = seq(0,n,1)[:,NewAxis]/n;
    theta = pi*seq(-n,n)/n;
    X = r*cos(theta);
    Y = r*sin(theta);
    C = r*cos(2*theta);
    pcolor(X,Y,C,axis='image')
    raw_input('press enter')
    
if __name__ == '__main__':
    test_2Dvector(); clf()
    test_2Dvector2(); clf()
    test_3Dvector(); clf()
    test2(); clf()
    test3(); clf()
    test_streamline(); clf()
    test_streamtube(); clf()
    test_streamribbon(); clf()
    test_slice_(); clf()
    test_slice_2(); clf()
    test_isosurface(); clf()
    my_test(); clf()
    test_plot(); clf()
    test_subplot(); clf()
    test_subplot2(); clf()
    matlab_test(); clf()
    matlab_test2(); clf()
    matlab_test3(); clf()
    #test_quiver()
    test_quiver3(); clf()
    test_figure(); clf()
    test_legend(); clf()
    test_contourf(); clf()
    test_lights(); clf()
    test_pcolor(); clf()
