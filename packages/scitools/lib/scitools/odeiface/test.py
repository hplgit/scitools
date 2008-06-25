from odesolve_unit import SciPyIntegrator

solver = SciPyIntegrator()

def myrhs(y,t,a,b):
	return [-a*y[0],-b*y[1]]

solver.set(f=myrhs, initial_condition=[1,1], f_args=(1,1))
y, t = solver.integrate(t0=2, T=4)

for y, t in zip(y, t):
    print t, "\t", y

#for i in range(len(rk4_t)):
#    print i, "\t", fwe_y[i], "\t", rk4_y[i]
