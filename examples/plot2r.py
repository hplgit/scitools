from scitools.std import *
import os, glob
for filename in glob.glob('tmp.*'):
    os.remove(filename)

def f1(t):
    return t**2*exp(-t**2)

def f2(t):
    return t**2*f1(t)

t = linspace(0, 3, 51)
y1 = f1(t)
y2 = f2(t)

plot(t, y1, 'r-', t, y2, 'b-',
     xlabel='t', ylabel='y',
     legend=('t^2*exp(-t^2)', 't^4*exp(-t^2)'),
     title='Plotting two curves in the same plot',
     savefig='.png')  # just .png implies tmp.png

# Return data (if possible, otherwise None) AND save to tmp.svg/tmp.png
# (just giving the extension implies returning the file data if the
# backend supports this - only matplotlib does)
figdata_svg = savefig('.svg')
figdata_png = savefig('.png')
if figdata_svg is not None and figdata_png is not None:
    import base64
    figdata_png = base64.b64encode(figdata_png)
    f = open('tmp.html', 'w')
    f.write("""
<h1>Demo of
<a href="http://msdn.microsoft.com/en-us/library/gg589526(v=vs.85).aspx">
SVG file in HTML</a> (plot made by %(backend)s)</h1>
Embedded SVG XML code:<br>
%(figdata_svg)s
<br>
Embedded PNG data:<br>
<img src="data:image/png;base64,%(figdata_png)s" width=500><br>
Using img tag for SVG file:<br>
<img alt="Embedded SVG image" src="tmp.svg" width=500><br>
Using img tag for PNG file:<br>
<img alt="Embedded PNG image" src="tmp.png" width=500><br>
Using object embedding:<br>
<object data="tmp.svg" type="image/svg+xml"></object>
""" % vars())
    f.close()
raw_input('Press Return key to quit: ')
