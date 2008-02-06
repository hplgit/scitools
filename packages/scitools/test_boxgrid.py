from scitools.BoxField import *
g = UniformBoxGrid.init_fromstring("[0,1]x[0,2] [0:25]x[0:10]")
if 0:
    func = lambda x,y: sin(x) *exp(y-x)
    a = g.vectorized_eval(lambda x,y: sin(x)*exp(y-x))
    d1 = UniformBoxGrid.init_fromstring("[0,20]x[0,10] [0:50]x[0:100]")
    u1 = d1.vectorized_eval(func)
#d2 = UniformBoxGrid.init_fromstring("[0,20]x[10,20] [0:50]x[0:100]")
#u2 = d2.vectorized_eval(func)
for i, j in g.iter('corners'):
    print g[i,j]
#for i, j in g.iter('all_boundary'): # Gives flat list instead of x,y pairs
#    print g[i,j]


#from scitools.all import *
g = UniformBoxGrid(x=(0,2), nx=2, y=(0,2), ny=2)
#values = g.coorv[0]*g.coorv[1]
#surf(values)
for i, j in g.iter('all'):
    print 'all:', i, j
    print 'all:', g.xcoor[i], g.ycoor[j]
for i, j in g.iter('interior'):
    print 'interior:', i, j
    print 'interior:', g.xcoor[i], g.ycoor[j]
for imin,imax, jmin,jmax in g.iter('all_boundary'):
    print 'all_boundary:', imin,imax, jmin,jmax
    print 'all_boundary:', \
          g.xcoor[imin],g.xcoor[imax], g.ycoor[jmin],g.ycoor[jmax]
for imin,imax, jmin,jmax in g.iter('interior_boundary'):
    print 'interior_boundary:', imin,imax, jmin,jmax
    print 'interior_boundary:', \
          g.xcoor[imin],g.xcoor[imax], g.ycoor[jmin],g.ycoor[jmax]
for i, j in g.iter('corners'):
    print 'corners:', i,j
    print 'corners:', g.xcoor[i], g.ycoor[j]
