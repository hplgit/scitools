#!/usr/bin/env python

import glob, os, time
from scitools.numpytools import *
from scipy import linspace
from utils import *

import sys
backend = os.environ.get('easyviz_backend','vtk_') # vtk backend default
legal_backends = 'vtk_ gnuplot_ pyx_ blt_'.split()
if len(sys.argv) > 1:
    if not sys.argv[1] in legal_backends:
        print "no such backend as %s, using default (vtk_)" % sys.argv[1]
    else:
        backend = sys.argv[1]
        sys.argv = sys.argv[:1] + sys.argv[2:]
try:
    exec('from easyviz.%s import *' % backend)
except:
    print 'could not import backend %s' % backend
    sys.exit(1)

def _test_labels():
    xx,yy,zz = get_data()

    print "testing labels..."
    mesh(zz, title='mesh with default labels', show=screenplot)
    show()
    next(clear_figure, prompt, pause, psplot)
    mesh(zz, title='mesh with new labels (using x-, y-, and zlabel methods)',
         show=screenplot)
    xlabel('x-axis'); ylabel('y-axis'); zlabel('z-axis')
    show()
    next(clear_figure, prompt, pause, psplot)
    surf(zz,title='surface with new labels (using keyword arguments)',
         xlabel='x2',ylabel='y2',zlabel='z2', show=screenplot)
    
def _test_axis():
    xx,yy,zz = get_data()

    print "testing axis using keyword arguments..."
    mesh(zz, show=screenplot, title="default axes")
    next(clear_figure, prompt, pause, psplot)
    mesh(xx,yy,zz,xmin=-.5,xmax=.5, title="mesh(xx,yy,zz,xmin=-.5,xmax=.5)",
         show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz, xmin=-5, xmax=50, ymin=-5, ymax=50, 
         title="mesh(zz,xmin=-5,xmax=50,ymin=-5,ymax=50)", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(xx,yy,zz, axis=[-5,5,-5,5,-15,15], 
         title="mesh(xx,yy,zz,axis=[-5,5,-5,5,-15,15]", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,axis='off', title="axes turned off", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,axis='on', title="axes turned on", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,axis='auto', title="axis='auto'", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,axis='manual', title="axis='manual'", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,axis='equal', title="axis='equal'", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,axis='tight', title="mesh(zz,axis='tight')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    print "testing axis using the axis method..."
    set(show=screenplot)
    surf(xx,yy,zz)
    axis(xmin=-.5,xmax=.5,ymin=-1,ymax=1)
    title("surf(xx,yy,zz); axis(xmin=-.5,xmax=.5,ymin=-1,ymax=1)")
    show()
    next(False, prompt, pause, psplot)
    axis([-5,5,-5,5,-15,15])
    title("axis([-5,5,-5,5,-15,15])")
    show()
    next(False, prompt, pause, psplot)
    axis('off')
    title("axis('off')")
    show()
    next(False, prompt, pause, psplot)
    axis('on')
    title("axis('on')")
    show()
    
    

def _test_view():
    xx,yy,zz = get_data()
    
    print "testing different views..."
    mesh(zz, title='view: default', hidden='on', show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,view=(40,70), title='view: (40,70)', hidden='on', show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    surf(zz, show=screenplot)
    hidden('on')
    title('view: (70,40)')
    view(70,40)
    show()
    next(clear_figure, prompt, pause, psplot)
    surf(zz,title='default 3D view', hidden='on', view=3, show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    surf(zz,title='default 2D view', hidden='on', view=2, show=screenplot)

def _test_quiver():
    xx,yy,zz = get_data(step=.5)
    xv = xx*ones(zz.shape)
    yv = yy*ones(zz.shape)
    uu = xv+1
    vv = yv+1
    
    print "testing quiver..."
    quiver(xx,yy,uu*0+.9,vv*0+.4, title="quiver(xx,yy,uu*0+.9,vv*0+.4)",
           show=screenplot)
    next(clear_figure, prompt, pause, psplot)
##     quiver(seq(len(ravel(xx))-1),yy,uu,vv,
##            title="quiver(seq(len(xx.flat)-1),yy,uu,vv)", show=screenplot)
##     next(clear_figure, prompt, pause, psplot)
    quiver(yv,xv,vv*0+.9,uu*0+.9, title="quiver(yv,xv,vv*0+.9,uu*0+.9)",
           show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    quiver(xx,yy,uu,vv, title="quiver(xx,yy,uu,vv)", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    quiver(uu,vv,'filled', 'g', title="quiver(uu,vv,'filled','g')",
           show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    quiver(uu,vv,'r:.', title="quiver(uu,vv,'r:.')",show=screenplot)

def _test_contours():
    xx,yy,zz = get_data()

    print "testing contours..."
    # testing contour(...):
    contour(xx,yy,zz,title="2D contour plot using contour(xx,yy,zz)",
            show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    contour(xx,yy,zz,20,
            title="2D contour plot with 20 levels using contour(xx,yy,zz,20)",
            show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    contour(xx,yy,zz,seq(arrmin(zz),arrmax(zz),1), 
            title="contour(xx,yy,zz,seq(arrmin(zz),arrmax(zz),1))",
            show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    contour(xx,yy,zz,[-0.2,-0.5,0.2,0.5], 
            title="contour(xx,yy,zz,[-0.2,-0.5,0.2,0.5])", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    contour(zz,15, clabels='on', title="contour(zz,clabels='on')",
            show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    # testing contour3(...):
    contour3(xx,yy,zz, title="3D contour plot using contour3(xx,yy,zz)",
             show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    contour3(xx,yy,zz,20, linewidth=2,
             title="20 contour leves using contour3(xx,yy,zz,20,linewidth=2)",
             show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    contour3(zz, 15, clabels='on', title="contour3(zz,15,clabels='on')",
             show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    # testing meshc(...):
    meshc(zz, hidden='on', title="Mesh with contours using meshc(zz)",
          show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    meshc(zz, clevels=20, hidden='on',
          title="20 contour levels using meshc(zz,clevels=20)",
          show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    # testing surfc(...):
    surfc(zz, hidden='on',
          title="Surface with contours using surfc(zz)", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    surfc(zz, cvector=[-0.2,-0.5,0.2,0.5], hidden='on',
          title="surfc(zz,cvector=[-0.2,-0.5,0.2,0.5])", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    
    surfc(zz, clevels=15, clabels='on', hidden='on', 
          title="surfc(zz,clevels=10,clabels='on')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    # testing contourf(...):
    contourf(xx,yy,zz, title='Filled contour plot using contourf(xx,yy,zz)')
    next(clear_figure, prompt, pause, psplot)
    contourf(zz,15, title='Filled contour plot using contourf(zz,15)')
    #next(clear_figure, prompt, pause, psplot)
    #contourf(zz,10, clabels='on', title="contourf(zz,10,clabels='on')")

def _test_colormaps():
    xx,yy,zz = get_data()
    
    # typical usage:
    # mesh(xx,yy,zz,colormap=hot())
    # or
    # colormap(hsv()); mesh(xx,yy,zz)

    colormaps = 'hsv,hot,gray,bone,copper,pink,white,flag,lines,colorcube,'\
                'jet,cool,autumn,spring,winter,summer'.split(',')

    print "testing colormaps..."
    # surf looks better in vtk:
    #if backend == 'vtk_':
    #    mesh = surf
    mesh(zz,title="colormap: default", show=screenplot)
    for cmap in colormaps:
        next(clear_figure, prompt, pause, psplot)
        try:
            exec('c=%s()' % cmap)
            mesh(zz,colormap=c,title="colormap: '%s'" % cmap,
                 colorbar='on', hidden='on', show=screenplot)
        except NotImplementedError, msg:
            print msg

def _test_caxis():
    xx,yy,zz = get_data()
    print "testing color axis scaling..."
    surf(zz, title="surf(zz); caxis(-2,2)", hidden='on', colorbar='on')
    caxis(-2,2)
    show()
    next(clear_figure, prompt, pause, psplot)
    surf(zz, caxis=[0,10], title="surf(zz,caxis=[0,10])", colorbar='on',
         show=screenplot)
    next(False, prompt, pause, psplot)
    set(show=False)
    caxis('manual')
    hold('on')
    surf(zz+10,
         title="surf(zz,caxis=[0,10]; caxis('manual'); hold('on'); surf(zz+10)",
         show=screenplot)
    next(False, prompt, pause, psplot)
    set(show=False)
    caxis('auto')
    title("caxis('auto')")
    set(show=screenplot)
    show()
    
def _test_box():
    xx,yy,zz = get_data()
    print "testing box around figure..."
    mesh(zz, box='on', title="mesh(zz,box='on')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz, box='off', title="mesh(zz,box='on')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,title="mesh(zz); box('on')", show=screenplot)
    box('on'); show()
    next(False, prompt, pause, psplot)
    title("box('off')"); box('off'); show()
    next(False, prompt, pause, psplot)
    title('box() (toggle on)'); box(); show()
    next(False, prompt, pause, psplot)
    title('box() (toggle off)'); box(); show()

def _test_grid():
    xx,yy,zz = get_data()
    print "testing grid..."
    mesh(zz, grid='on' ,title="mesh(zz,grid='on')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz, grid='off', title="mesh(zz,grid='off')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    mesh(zz,title="mesh(zz); grid('on')", show=screenplot)
    grid('on'); show()
    next(False, prompt, pause, psplot)
    title("grid('off')"); grid('off'); show()
    next(False, prompt, pause, psplot)
    title('grid() (toggle on)'); grid(); show()
    next(False, prompt, pause, psplot)    
    title('grid() (toggle off)'); grid(); show()
    
def _test_colorbar():
    xx,yy,zz = get_data()
    cblocations = 'North South East West NorthOutside SouthOutside ' \
                  'EastOutside WestOutside'.split()
    print "testing colorbar..."
    for cbloc in cblocations:
        mesh(zz,colorbar='on',cblocation=cbloc,
             title="colorbar location: '%s'" % cbloc, show=screenplot)
        next(clear_figure, prompt, pause, psplot)

def _test_figure():
    x=seq(-2,2,.1)
    plot(x**2, title="Plotting into figure 1: plot(x**2)")
    #f1=gcf()
    next(False, prompt, pause, psplot)
    
    figure(2)
    plot(x,x**3,'r', title="Plotting into figure 2: plot(x,x**3,'r')")
    #f2=gcf()
    next(False, prompt, pause, psplot)

    figure(1)
    plot(x,x,'r', title="Plotting into figure 1: plot(x,x)")

def _test_hardcopy_only():
    xx,yy,zz = get_data()
    
    surfc(zz,
          clabels='on',
          clevels=10,
          hidden='on',
          xlabel='x-axis', ylabel='y-axis', zlabel='z-axis',
          title='Test of the Peaks function.',
          colormap=hsv(),
          colorbar='on',
          cblocation='SouthOutside',
          shading='interp',
          show=False)
    hardcopy(filename='tmp_easyviz_hardcopy_only.ps', color=True,
             fontname='Helvetica', fontsize=18)
    show()
    set(show=screenplot)

def _test_plot3():
    print 'testing plot3...'
    t = seq(0,10*pi,pi/50)
    plot3(sin(t),cos(t),t, title="plot3(sin(t),cos(t),t)", grid='on',
          show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    x = seq(-2,2,.1)
    plot3(x,x,x, x,x,x**2, x,x,x**3, view=(20,40), grid=1,
          title="plot3(x,x,x, x,x,x**2, x,x,x**3)", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    
    plot3(x,x,x,'r', x,x,x**2,'b', x,x,x**3,'g', view=(20,40), grid=1,
          title="plot3(x,x,x,'r', x,x,x**2,'b', x,x,x**3,'g')",
          show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    
    plot3(x,'r', x**2,'b', x**3,'g', view=(20,40), grid=1,
          title="plot3(x,'r', x**2,'b', x**3,'g')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    
    plot3(x, x**2, x**3, x='auto', y='auto', view=(20,40), grid=1,
          title="plot3(x, x**2, x**3, x='auto', y='auto')", show=screenplot)
    next(clear_figure, prompt, pause, psplot)
    
    plot3(x,'m', x**2,'k', x**3,'c', x='auto', y='auto', view=(20,40), grid=1,
          title="plot3(x,'m', x**2,'k', x**3,'c', x='auto', y='auto')",
          show=screenplot)

def _test_legend():
    x=seq(-2,2,.2)
    colors = 'r g b c m y k'.split()
    hold('on')
    for i in range(len(colors)):
        plot(x,x+i,'%s'%colors[i],legend='x+%d'%i)

def _test_lights():
    x=seq(-3,3,.1)
    xx,yy=meshgrid(x,x)
    zz=peaks(xx,yy)
    surf(zz,title='No lights')
    next(clear_figure, prompt, pause, psplot)
    
    surf(zz,light=Light(),title='default light')
    next(clear_figure, prompt, pause, psplot)
    
    surf(zz,light=Light(lightpos=(-10,-10,10),lightcolor=(.5,.5,.5)),
         title='light at (-10,-10,10) and color (0,0,1)')
    next(clear_figure, prompt, pause, psplot)
    
    surf(zz,title='No lights')

def _test_pcolor():
    n = 6;
    r = seq(0,n,1)[:,NewAxis]/n;
    theta = pi*seq(-n,n)/n;
    X = r*cos(theta);
    Y = r*sin(theta);
    C = r*cos(2*theta);
    pcolor(X,Y,C,
           axis='image',
           title='pcolor plot')
    
def _test_subplot():
    xx,yy,zz = get_data(step=.2)
    
    print "testing subplot..."
    #set(show=False)
    subplot(1,2,1)
    surf(xx,yy,xx*yy, hidden=1, title='subplot(1,2,1); surf(xx,yy,xx*yy)',
         show=screenplot)
    subplot(1,2,2)
    surf(xx,yy,xx*xx*ones(zz.shape), hidden=1,
         title='subplot(1,2,2); surf(xx,yy,xx*xx)',
         show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    subplot(2,1,2)
    xv = xx*ones(zz.shape)
    yv = yy*ones(zz.shape)
    quiver(xv,yv,'b', title="subplot(2,1,2); quiver(xx,yy,'b')",
           show=screenplot)
    subplot(2,1,1)
    plot([1,2,3],'bo-',[4,5,6],'rx-', show=screenplot)
    subplot(2,1,2)
    mesh(zz, show=screenplot)
    next(clear_figure, prompt, pause, psplot)

    subplot(2,2,1)
    surf(xx,yy,xx*xx*ones(zz.shape),
         title="subplot(2,2,1); surf(xx,yy,xx*xx)", 
         hidden=1, show=screenplot)
    subplot(2,2,2)
    surf(xx,yy,-yy*yy*ones(zz.shape),
         title="subplot(2,2,2); surf(xx,yy,-yy*yy)", 
         hidden=1, show=screenplot)
    subplot(2,2,3)
    surf(xx,yy,xx*yy, title="subplot(2,2,3); surf(xx,yy,xx*yy)",
         hidden=1, show=screenplot)
    subplot(2,2,4)
    surf(xx,yy,xx**2+yy**2, title="subplot(2,2,4); surf(xx**2+yy**2)",
         hidden=1, show=screenplot)

def _test_subplot2():
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
    next(clear_figure, prompt, pause, psplot)

    subplot(2,2,2)
    x=linspace(0,3,80); y=sin(2*pi*x); theta=2*pi*x+pi/2;
    quiver(x,y,sin(theta)/10,cos(theta)/10,0.04,'b')
    hold('on'); plot(x,y,'r'); hold('off')
    next(clear_figure, prompt, pause, psplot)

    subplot(2,2,3)
    x = seq(-8,8,.2)
    xx,yy = meshgrid(x,x)
    r = sqrt(xx**2+yy**2) + 0.01
    zz = sin(r)/r
    surfc(xx,yy,zz,colormap=jet(),colorbar='on',cbtitle='test',
          zmin=-0.5,zmax=1,clevels=10,
          shading='interp',
          title='r=sqrt(x**2+y**2)+eps, sin(r)/r',
          light=Light(position=(-10,-10,5)),
          )
    next(clear_figure, prompt, pause, psplot)

    subplot(2,2,4)

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

def _test_streamribbon():
    xmin = -7; xmax = 7
    ymin = -7; ymax = 7 
    zmin = -7; zmax = 7 
    x = linspace(xmin,xmax,20)
    y = linspace(ymin,ymax,30)
    z = linspace(zmin,zmax,20)
    x,y,z = meshgrid(x,y,z)
    nx, ny, nz = x.shape[0], y.shape[1], z.shape[2]
    x = x*ones((nx,ny,nz))
    y = y*ones((nx,ny,nz))
    z = z*ones((nx,ny,nz))
    tmp = x.copy()
    x = y
    y = tmp
    u = y*ones((nx,ny,nz))
    v = -x*ones((nx,ny,nz))
    w = 0*x*ones((nx,ny,nz))+1

    set(show=False)
    hold('on')
    daspect([1,1,1])
    cx,cy,cz = meshgrid(linspace(xmin,xmax,30),linspace(ymin,ymax,30),[-3,4])
    #h2=coneplot(x,y,z,u,v,w,cx,cy,cz, 'q')
    #set(h2, 'color', 'k');
      
    sx,sy,sz = meshgrid(seq(-1,1),seq(-1,1),array([-6]*3))
    sx = sx*ones((3,3,3))
    sy = sy*ones((3,3,3))
    sz = sz*ones((3,3,3))
    p = streamribbon(x,y,z,u,v,w,sx,sy,sz)
    sx,sy,sz = meshgrid(seq(1,6),zeros(6,Float),array([-6]*6))
    sx = sx*ones((6,6,6))
    sy = sy*ones((6,6,6))
    sz = sz*ones((6,6,6))
    p2 = streamribbon(x,y,z,u,v,w,sx,sy,sz,
                      view=3,
                      shading='interp',
                      camproj='perspective')
      
    #view(-30,10); axis('off'); axis('tight')
    #camproj p; camva(66); camlookat; camdolly(0,0,.5,'f')
    #camlight
    set(show=True)
    show()

def _test_streamtube():
    x = seq(-2,2,1)
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    px,py,pz = gradient(vv)
    streamtube(xx,yy,zz,px,py,pz,[0.1]*5,[-.5,-.2,0,.1,.5],seq(-2,2,1),
               #zmin=-.2,zmax=.2,
               daspect=[1,1,1],
               view=3,
               )

def _test_streamline():
    x = seq(-2,2,.2)
    xx,yy = meshgrid(x,x)
    zz = xx*exp(-xx**2-yy**2)
    px,py = gradient(zz)
    print "testing streamlines..."
    streamline(xx,yy,px,py,[.2,-.2],[-.5,-.5],.2,
               title='streamlines (plus vector and contour plot)',
               hold='on')
    quiver(xx,yy,px,py,4)
    contour(xx,yy,zz,10)
    
    next(clear_figure, prompt, pause, psplot)
    hold('off')
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    px,py,pz = gradient(vv)
    streamline(xx,yy,zz,px,py,pz,x,x,x,title='more streamlines')

def _test_slice_():
    #xx,yy,zz = meshgrid(seq(-2,2,.2), seq(-2,2,.25), seq(-2,2,.16))
    x = seq(-2,2,.2)
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    slice_(xx, yy, zz, vv, [-1.2,.8,2], 2, [-2,-.2],
           #shading='interp',
           colormap=jet(),
           title='slices at x=[-1.2, .8, 2], y=2, and z=[-2, -.2]'
           )
    #slice_(xx, yy, zz, vv, 0, 0, 0, shading='faceted')
    
    next(clear_figure, prompt, pause, psplot)
    x2 = seq(-1,1,.2)
    xv,yv = meshgrid(x,x)
    xv = xv*ones([len(x)]*2)
    yv = yv*ones([len(x)]*2)
    zv = peaks(xv,yv)
    slice_(xx, yy, zz, vv, xv, yv, zv,
           #shading='interp',
           colormap=jet(),
           title='slices with surface (peaks)'
           )

def _test_isosurface():
    x = seq(-2,2,.2)
    xx,yy,zz=meshgrid(x,x,x)
    vv = xx*exp(-xx**2-yy**2-zz**2)
    isosurface(xx,yy,zz,vv,0.001,hold='on')
    isosurface(xx,yy,zz,vv,-0.1,
               shading='interp',
               colormap='hsv',
               title='isosurface with isovalue at 0.001 and -0.1')

    next(clear_figure, prompt, pause, psplot)
    hold('off')
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

def _test_shading():
    xx,yy,zz = get_data()
    print "testing different shadings..."
    surf(zz,shading='faceted',title="shading: 'faceted' (default)")
    next(clear_figure, prompt, pause, psplot)
    surf(zz,shading='flat',title="shading: 'flat'")
    next(clear_figure, prompt, pause, psplot)
    surf(zz,shading='interp',title="shading: 'interp'")

def _test_quiver3():
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
            xmin=0,xmax=3.5,ymin=0,ymax=3,zmin=-10,zmax=2,
            show=screenplot,
            )
    next(clear_figure, prompt, pause, psplot)
    
    x = seq(-3,3,1)
    xx,yy,zz = meshgrid(x,x,x)
    nx, ny, nz = shape(xx+yy+zz)
    xv = xx*ones((1,ny,nz))
    yv = yy*ones((nx,1,nz))
    zv = zz*ones((nx,ny,1))
    quiver3(xv,yv,zv,xv,yv,zv,'r',
            view=3,
            axis=[-5,5,-5,5,-5,5],
            daspect=[1,1,1],
            grid='on',
            show=screenplot,
            )
    next(clear_figure, prompt, pause, psplot)

    x = seq(-2,2,1)
    xx,yy=meshgrid(x,x)
    zz = xx*exp(-xx**2-yy**2)
    uu = array([[0.0125,   -0.0003,   -0.0067,   -0.0003,    0.0125],
                [0.2429,   -0.0066,   -0.1341,   -0.0066,    0.2429],
                [0.5628,   -0.0183,   -0.3453,   -0.0183,    0.5628],
                [0.2429,   -0.0066,   -0.1341,   -0.0066,    0.2429],
                [0.0125,   -0.0003,   -0.0067,   -0.0003,    0.0125]])
    vv = array([[0.0076,    0.0764,         0,   -0.0764,   -0.0076],
                [0.0174,    0.1777,         0,   -0.1777,   -0.0174],
                [     0,         0,         0,         0,         0],
                [-0.0174,  -0.1777,         0,    0.1777,    0.0174],
                [-0.0076,  -0.0764,         0,    0.0764,    0.0076]])
    ww = array([[0.9999,    0.9971,    1.0000,    0.9971,    0.9999],
                [0.9699,    0.9841,    0.9910,    0.9841,    0.9699],
                [0.8266,    0.9998,    0.9385,    0.9998,    0.8266],
                [0.9699,    0.9841,    0.9910,    0.9841,    0.9699],
                [0.9999,    0.9971,    1.0000,    0.9971,    0.9999]])

    quiver3(xx,yy,zz,uu,vv,ww)
    hold('on')
    surf(xx,yy,zz)


def next(clear_figure=False, prompt='next plot', pause=0,
         save_hardcopy=False):
    if save_hardcopy:
        global hardcopy_counter
        hardcopy(filename='tmp_easyviz_plot%03d.ps' % hardcopy_counter,
                 color=True, fontname='Helvetica', fontsize=18)
        hardcopy_counter += 1
    if prompt:
        raw_input(prompt)
    if pause:
        time.sleep(pause)
    if clear_figure:
        clf()

def get_data(step=.1):
    x = seq(-2,2,step)
    xx,yy = meshgrid(x,x)
    zz = peaks(xx,yy)
    return xx,yy,zz    

def _tests(clear_figure, prompt, pause, psplot):
    _test_labels(); next(clear_figure, prompt, pause, psplot)
    _test_axis(); next(clear_figure, prompt, pause, psplot)
    _test_view(); next(clear_figure, prompt, pause, psplot)
    _test_quiver(); next(clear_figure, prompt, pause, psplot)
    _test_contours(); next(clear_figure, prompt, pause, psplot)
    _test_colormaps(); next(clear_figure, prompt, pause, psplot)
    _test_caxis(); next(clear_figure, prompt, pause, psplot)
    _test_box(); next(clear_figure, prompt, pause, psplot)
    _test_grid(); next(clear_figure, prompt, pause, psplot)
    _test_colorbar(); next(clear_figure, prompt, pause, psplot)
    _test_figure(); next(clear_figure, prompt, pause, psplot)
    _test_hardcopy_only(); next(clear_figure, prompt, pause, psplot)

    if backend in ['vtk_', 'gnuplot_']:
        _test_plot3(); next(clear_figure, prompt, pause, psplot)
        _test_subplot(); next(clear_figure, prompt, pause, psplot)

    if backend in ['vtk_']:
        _test_pcolor(); next(clear_figure, prompt, pause, psplot)
        _test_quiver3(); next(clear_figure, prompt, pause, psplot)
        _test_shading(); next(clear_figure, prompt, pause, psplot)
        _test_streamline(); next(clear_figure, prompt, pause, psplot)
        _test_slice_(); next(clear_figure, prompt, pause, psplot)
        _test_isosurface(); next(clear_figure, prompt, pause, psplot)
        _test_subplot2(); next(clear_figure, prompt, pause, psplot)
        _test_streamribbon(); next(clear_figure, prompt, pause, psplot)
        _test_streamtube(); next(clear_figure, prompt, pause, psplot)
        _test_lights(); next(clear_figure, prompt, pause, psplot)
        # why is the streamribbon object still present in ax.plotitems???
        gca()._prop['plotitems'] = []
        _test_legend(); next(clear_figure, prompt, pause, psplot)
    
if __name__ == '__main__':
    # command-line arguments: n screenplot flash psplot
    # screenplot: show plots on the screen?
    # flash: drop prompt between plots and clf, everything goes into one plot
    # psplot: make hardcopy of each plot?

    # 1 0 1 1 gives execution in batch without user interaction
    
    import sys
    global hardcopy_counter, clear_figure, prompt, pause, psplot, screenplot
    try: n = int(sys.argv[1])
    except: n = 1
    try: screenplot = bool(int(sys.argv[2]))
    except: screenplot = True
    try: flash = bool(int(sys.argv[3]))
    except: flash = True
    try: psplot = bool(int(sys.argv[4]))
    except: psplot = True

    hardcopy_counter = 0
    if flash:
        # let all plots flash on the screen with 1 s pause
        clear_figure = False
        prompt = ''
        pause = 1
    else:
        # press return for each plot on the screen
        clear_figure = False
        prompt = 'next test'
        pause = 0
    #_tests(clear_figure, prompt, pause, psplot)
    _tests(True, prompt, pause, psplot)
