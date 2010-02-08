#!/usr/bin/env python

# Simple diagnostic tool for scitools.easyviz

import os, sys
import time, glob
import platform
import pprint
import signal
import ctypes
from subprocess import Popen, PIPE, STDOUT

# Taken from
# http://ivory.idyll.org/blog/mar-07/replacing-commands-with-subprocess
def get_status_output_errors(cmd, input=None, cwd=None, env=None):
    pipe = Popen(cmd, shell=True, cwd=cwd, env=env, stdout=PIPE, stderr=PIPE)

    output, errout = pipe.communicate(input=input)

    status = pipe.returncode

    return status, output, errout

def message(msg, diag_file=None, stdout=True):
    if stdout:
        print msg,
        sys.stdout.flush()
    if isinstance(diag_file, file) and not diag_file.closed:
        diag_file.write(msg)

def wait(str=None, prompt='Press return to show results...\n'):
    if str is not None:
        print str
    raw_input(prompt)

def wait(seconds=1):
    time.sleep(seconds)

def test_scitools():
    import scitools
    print "SciTools is installed in", os.path.dirname(scitools.__file__)
    print "SciTools version", scitools.__version__
    
    from scitools.configdata import config_parser_frontend
    config_data, files = config_parser_frontend('scitools', os.curdir)
    print "Values from scitools.cfg:"
    pprint.pprint(config_data)
    pprint.pprint(files)

def test_numpy():
    import numpy
    #numpy.test()

def test_numeric():
    import Numeric
    print "Numeric is installed in", os.path.dirname(Numeric.__file__)
    print "Numeric version", Numeric.__version__

def test_numarray():
    import numarray
    print "numarray is installed in", os.path.dirname(numarray.__file__)
    print "numarray version", numarray.__version__

def test_scipy():
    import scipy
    print "SciPy is installed in", os.path.dirname(scipy.__file__)
    print "SciPy version", scipy.version.version
    #scipy.test()

def test_blt():
    import Pmw
    import Tkinter

    print "Pmw is installed in", os.path.dirname(Pmw.Blt.__file__)
    print "Pmw version", Pmw.version()
    print "Tkinter is installed in", os.path.dirname(Tkinter.__file__)
    print "Tkinter version", Tkinter.__version__

    master = Tkinter.Tk()
    master.withdraw()

    root = Tkinter.Toplevel(master)
    root.title("Hello BLT!")
    root.geometry('320x240')
    
    def close_window(event=None):
        root.withdraw()
    root.protocol("WM_DELETE_WINDOW", close_window)
    root.bind("<KeyPress-q>", close_window)
    
    frame = Tkinter.Frame(root)
    frame.pack(side='top', fill='both', expand=1)

    g = Pmw.Blt.Graph(frame)
    g.pack(expand=1, fill='both')

    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    g.line_create('x^2', xdata=tuple(x), ydata=tuple(y))

    g.update()

    wait()

def test_dx():
    import DX
    import Tkinter
    import tempfile

    DXMACROS = '/usr/share/dx/samples/macros'
    DXMACROS = os.environ.get('DXMACROS', DXMACROS)

    master = Tkinter.Tk()
    master.withdraw()
    root = Tkinter.Toplevel(master)
    root.title("Hello OpenDX!")
    def close_window(event=None):
        root.withdraw()
    root.protocol("WM_DELETE_WINDOW", close_window)
    root.bind("<KeyPress-q>", close_window)
    root.geometry('320x240')
    root.withdraw()
    frame = Tkinter.Frame(root, relief='sunken', bd=2)
    frame.pack(side='top', fill='both', expand=1)

    # start DX:
    cmd = DX.DXEXEC + ' -execonly -hwrender opengl'
    conn = DX.DXLStartDX(cmd, None)

    #DX.DXLLoadMacroDirectory(self.conn, DXMACROS)
    # hack for loading necessary macro files:
    DX.exDXLLoadScript(conn, os.path.join(DXMACROS, "ArrangeMemberMacro.net"))
    DX.exDXLLoadScript(conn, os.path.join(DXMACROS, "CappedIsoMacro.net"))


    root.deiconify()
    root.update()
    DX.DXLExecuteOnChange(conn)
    DX.WaitForDXIdle(conn)

def test_gnuplot():
    import Gnuplot

    gnuplot_command = Gnuplot.GnuplotOpts.gnuplot_command
    failure, out, err = get_status_output_errors(gnuplot_command + " --version")
    if failure:
        pass  # gnuplot command probably missing, will fail later

    print "Gnuplot.py is installed in", os.path.dirname(Gnuplot.__file__)
    print "Gnuplot.py version", Gnuplot.__version__
    print "Gnuplot version", out

    print "Values for some Gnuplot.py options:"
    for opt, value in Gnuplot.GnuplotOpts.__dict__.items():
        if opt == '__doc__':
            continue
        print "%s: %s" % (opt, value)
    print

    g = Gnuplot.Gnuplot(debug=1)
    g('set title "Hello Gnuplot!"')
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    data = Gnuplot.Data(x, y, with_='lines')
    g.plot(data)
    wait()
    g.close()

def test_matplotlib():
    import matplotlib
    import matplotlib.colors

    # Override system defaults before importing pylab
    matplotlib.use('TkAgg')
    #matplotlib.rc('text', usetex=True)
    matplotlib.interactive(True)
    from matplotlib.font_manager import fontManager, FontProperties
    import pylab

    print "matplotlib is installed in", os.path.dirname(matplotlib.__file__)
    print "matplotlib version", matplotlib.__version__
    print "matplotlib.rcParams:"
    pprint.pprint(matplotlib.rcParams)

    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    pylab.plot(x, y, 'bo-', linewidth=2.0)

    pylab.title("Hello Matplotlib!")

    pylab.draw()
    #pylab.show()  # requires manual quit of plot window
    time.sleep(0.5)

def test_mlabwrap():
    try:
        from scikits import mlabwrap
        from scikits.mlabwrap import mlab
    except ImportError, msg:
        print "Unable to find module scikits or scikits.mlabwrap"
        print "Error:\n", msg
        try:
            import mlabwrap
            from mlabwrap import mlab
        except ImportError, msg:
            # mlabwrap is not available
            print "Unable to find module mlabwrap"
            print "Error:\n", msg
            sys.exit(1)

    print "mlabwrap is installed in", os.path.dirname(mlabwrap.__file__)
    print "mlabwrap version", "unknown"
    print "MLABRAW_CMD_STR:", os.getenv("MLABRAW_CMD_STR")

    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]

    mlab.plot(x, y)

    mlab.title("Hello mlabwrap!")

    wait()

def test_visit():
    import visit

    VISIT_ARGS = os.environ.get('VISIT_ARGS', ["-nosplash"])
    if isinstance(VISIT_ARGS, str):
        VISIT_ARGS = VISIT_ARGS.split()
    for arg in VISIT_ARGS:
        visit.AddArgument(arg)
    visit.Launch()

    print "visit is installed in", os.path.dirname(visit.__file__)
    print "visit version", visit.Version()

    visit.ResetView()
    v3D = visit.GetView3D()
    v3D.SetViewUp(0,0,1)
    v3D.SetViewNormal(-0.5,-0.8,0.4)
    v3D.SetImageZoom(1.0)
    visit.SetView3D(v3D)

    aa = visit.AnnotationAttributes()
    aa.SetAxesType(2)  # outside edges
    aa.SetDatabaseInfoFlag(False)
    aa.SetUserInfoFlag(False)
    visit.SetAnnotationAttributes(aa)

    t = visit.CreateAnnotationObject("Text2D")
    t.SetText("Hello VisIt!")
    t.SetPosition(0.4,0.9)  # (0,0) is lower left corner
    t.SetFontFamily(0)      # 0: Arial, 1: Courier, 2: Times
    t.SetWidth(0.25)        # 25%
    t.SetTextColor((0,0,0)) 
    t.SetUseForegroundForTextColor(False)
    t.SetVisible(True)

    visit.OpenDatabase("tmp_.vtk")

    visit.AddPlot("Mesh", "scalars")
    ma = visit.MeshAttributes()
    visit.SetPlotOptions(ma)
    visit.AddPlot("Pseudocolor", "scalars")
    pa = visit.PseudocolorAttributes()
    visit.SetPlotOptions(pa)

    visit.RedrawWindow()
    visit.DrawPlots()

    wait()

def test_vtk():
    import vtk
    import Tkinter
    try:
        from vtkTkRenderWidget import vktTkRenderWidget
    except:
        from vtk.tk.vtkTkRenderWidget import vtkTkRenderWidget

    print "vtk is installed in", os.path.dirname(vtk.__file__)
    print "vtk version", vtk.vtkVersion().GetVTKVersion()

    # Create a sphere source, mapper, and actor
    sphere = vtk.vtkSphereSource()

    sphereMapper = vtk.vtkPolyDataMapper()
    sphereMapper.SetInputConnection(sphere.GetOutputPort())
    sphereMapper.GlobalImmediateModeRenderingOn()
    sphereActor = vtk.vtkLODActor()
    sphereActor.SetMapper(sphereMapper)

    # Create a scaled text actor. 
    # Set the text, font, justification, and properties (bold, italics,
    # etc.).
    textActor = vtk.vtkTextActor()
    textActor.ScaledTextOn()
    textActor.SetDisplayPosition(90, 50)
    textActor.SetInput("Hello VTK!")

    # Set coordinates to match the old vtkScaledTextActor default value
    textActor.GetPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
    textActor.GetPosition2Coordinate().SetValue(0.6, 0.1)

    tprop = textActor.GetTextProperty()
    tprop.SetFontSize(24)
    tprop.SetFontFamilyToArial()
    tprop.SetJustificationToCentered()
    tprop.BoldOn()
    tprop.ItalicOn()
    tprop.ShadowOn()
    tprop.SetColor(0, 0, 1)

    # Create the Renderer, RenderWindow, RenderWindowInteractor
    master = Tkinter.Tk()
    master.withdraw()
    root = Tkinter.Toplevel(master)
    root.title("Hello VTK!")
    def close(event=None):
        root.withdraw()
    root.bind("<KeyPress-q>", close)
    frame = Tkinter.Frame(root, relief='sunken', bd=2)
    frame.pack(side='top', fill='both', expand=1)
    tkw = vtkTkRenderWidget(frame, width=320, height=240)
    tkw.pack(expand='true', fill='both')
    
    ren = vtk.vtkRenderer()
    renwin = tkw.GetRenderWindow()
    renwin.AddRenderer(ren)

    # Add the actors to the renderer; set the background and size; zoom
    # in; and render.
    ren.AddActor2D(textActor)
    ren.AddActor(sphereActor)

    ren.SetBackground(1, 1, 1)
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.5)

    root.update()
    renwin.Render()

    wait()

def test_pyx():
    import math
    import pyx

    print "PyX is installed in", os.path.dirname(pyx.__file__)
    print "PyX version", pyx.__version__

    g = pyx.canvas.canvas()
    g.items = []

    xpos = 0
    ypos = 0
    width = 15
    ratio = 0.5*(math.sqrt(5)+1)  # golden mean
    height = (1.0/ratio)*width
    
    graph = pyx.graph.graphxy(xpos, ypos, width=width, height=height)
    g.insert(graph)  # insert graph into figure canvas
    g1 = g.items[-1]

    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    data = []
    for i in range(len(x)):
        data.append([x[i], y[i]])

    color = pyx.graph.style.color.cmyk.Blue
    styles = [pyx.graph.style.line([color])]
    g1.plot(pyx.graph.data.points(data, x=1, y=2), styles=styles)

    g1.text(g1.width/2+g1.xpos, g1.height+0.2+g1.ypos, "Hello PyX!",
            [pyx.text.halign.center,
             pyx.text.valign.bottom,
             pyx.text.size.Large])
    g.writetofile('tmp_pyx_.eps')

def test_grace(): 
    try:
        import grace_np
    except ImportError, msg:
        print "Unable to find module grace_np"
        print "Error:\n", msg
        try:
            import pygrace
            from pygrace import grace_np
        except ImportError:
            # grace_np is not available
            print "Unable to find module grace_np"
            print "Error:\n", msg
            sys.exit(1)

    g = grace_np.GraceProcess()
    g('arrange(1, 1, 0.1, 0.5, 0.6)')
    g('with g%s' % 0)
    g('g%s on' % 0)

    g('s0 on')
    g('s0 symbol 9')  # cross
    g('s0 symbol fill pattern 0')
    g('s0 symbol size 0.6')
    g('s0 symbol color 4')  # blue symbol
    g('s0 line color 2') # red line
    g('s0 linestyle 1')  # solid line

    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    for i in range(len(x)):
        g('s0 point %s, %s' % (x[i], y[i]))
    g('autoscale')

    g('title "Hello Grace!"')
    g('redraw')
    
    wait()
    g('exit')

def test_veusz():
    import veusz
    import veusz.utils

    print "Veusz is installed in", os.path.dirname(veusz.__file__)
    print "Veusz version", veusz.utils.version()

    import veusz.embed
    g = veusz.embed.Embedded()
    g.EnableToolbar(enable=True)
    #g.window.hide()
    
    g.To('/')
    g.To(g.Add('page'))
    g.To('/page1')
    g.To(g.Add('graph'))

    xy = g.Add('xy')
    ## g.Set('%s/PlotLine/color' % xy, color)
    ## g.Set('%s/PlotLine/style' % xy, style)
    ## g.Set('%s/marker' % xy, marker)
    ## g.Set('%s/MarkerLine/color' % xy, color)
    ## g.Set('%s/MarkerFill/hide' % xy, True)

    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    g.SetData('x1', x)
    g.SetData('y1', y)
    g.Set('%s/xData' % xy, 'x1')
    g.Set('%s/yData' % xy, 'y1')

    label = g.Add('label')
    g.Set('%s/label' % label, "Hello Veusz!")
    g.Set('%s/xPos' % label, 0.2)
    g.Set('%s/yPos' % label, 0.9)

    g.Set('Background/hide', True)
    g.window.showNormal()

    wait(2)

def test_easyviz():
    from scitools.std import linspace, ndgrid, plot, contour, peaks, \
         quiver, surfc, backend, get_backend
    n = 21
    x = linspace(-3, 3, n)
    xx, yy = ndgrid(x, x, sparse=False)

    # a basic plot
    plot(x, x**2, 'bx:')
    wait()

    if backend in ['gnuplot', 'vtk', 'matlab', 'dx', 'visit', 'veusz']:
        # a contour plot
        contour(peaks(n), title="contour plot")
        wait()

        # a vector plot
        uu = yy
        vv = xx
        quiver(xx, yy, uu, vv)
        wait()

        # a surface plot with contours
        zz = peaks(xx, yy)
        surfc(xx, yy, zz, colorbar=True)
        wait()

    if backend == 'grace':
        g = get_backend()
        g('exit')

def test_dx():
    raise NotImplementedError('Tests for dx not implemented')

def test_latex():
    latexfile = 'tmp___latex'
    f = open(latexfile + '.tex', 'w')
    f.write(r"""
\documentclass{article}
\begin{document}
\[ \sin(x) = \sqrt{1 - \cos^2(x)} \]
\end{document}
""")
    f.close()
    status, outout, errout = get_status_output_errors('latex ' + latexfile)
    for filename in glob.glob(latexfile + '.*'):
        os.remove(filename)
    print 'status:', status, isinstance(status, int)
    if status != 0:
        raise Exception('status=%d, latex does not work: ' % status + outout)
          
def run():
    if not os.path.isfile('diagnostic.py'):
        print 'diagonstic.py must be run from the directory where it is located!'
        sys.exit(1)

    diag_fname = 'scitools_diagnostic.log'
    diag_file = open(diag_fname, 'w')

    #from scitools.misc import hardware_info
    #import pprint; pprint.pprint(hardware_info())
      
    # Write some info about the system to diag file:
    message("%s\n" % sys.version, diag_file, False)
    message("%s\n" % ' '.join(platform.uname()), diag_file, False)

    backends = ['blt', 'dx', 'gnuplot', 'grace', 'matplotlib',
                 'mlabwrap', 'pyx', 'veusz', 'visit', 'vtk']
    all_tests = ['scitools', 'numpy', 'scipy', 'latex'] + backends
                 
    for test in all_tests:
        message("\n" + "-"*30 + test + "-"*30 + "\n", diag_file, False)
        message("Running tests for %s..." % test, diag_file)
        cmd = 'python -c "import diagnostic; diagnostic.test_%s()"' % test
        failure, out, err = get_status_output_errors(cmd)
        if failure:
            message("failed\n", diag_file)
            message("Output:\n" + out, diag_file, False)
            message("Error:\n" + err, diag_file, False)
        else:
            message("ok\n", diag_file)
            message("Output:\n" + out, diag_file, False)
            if test in backends:
                message("Testing %s backend in Easyivz..." % test, diag_file)
                cmd = 'python -c "import diagnostic;' \
                      'diagnostic.test_easyviz()" ' \
                      '--SCITOOLS_easyviz_backend %s' % test
                failure, out, err = get_status_output_errors(cmd)
                if failure:
                    message("failed\n", diag_file)
                    message("Output:\n" + out, diag_file, False)
                    message("Error:\n" + err, diag_file, False)
                else:
                    message("ok\n", diag_file)
                    message("Output:\n" + out, diag_file, False)
        message("\n", diag_file, False)
            
    diag_file.close()
    message("See %s for details." % diag_fname)

if __name__ == '__main__':
    run()
