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
for i, j in g.iter('all_boundary'): # Gives flat list instead of x,y pairs
    print g[i,j]
