#!/usr/bin/env python

from scitools.std import *

# We start with a simple example using the plot command:

x = linspace(-2,2,5)
plot(x,x**2,'b-s',title='Simple plot')
print get_script()

# As we can see, the result is no output. This is because the _replot method
# has not been called yet. However, we don't need to call this method
# explicitly. Instead we should call either show or hardcopy (both of which
# calls _replot). Here we use show:

show()
print get_script()

# We can now store these commands in a Matlab script by calling the save_m
# function:

save_m('mytest.m')

# In this case, the file mytest.m will be placed in the current working
# directory and we can then run the file in Matlab, e.g., with the following
# statement:

os.system("matlab -nojvm -nosplash -r mytest")

# Note that we skip the extension of the file name (.m). To get back to the
# Python prompt, we must first exit Matlab.

# Now we create a contour plot in combination with a quiver plot:

reset()  # remove the previous Matlab commands
xx, yy = ndgrid(linspace(-3,3,51), linspace(-3,3,51), sparse=False)
zz = peaks(xx, yy)
contour(xx,yy,zz,12,hold='on')
uu, vv = gradient(zz)
quiver(xx,yy,uu,vv,hold='off')
hardcopy('tmp0.ps',color=True)
save_m('mytest2.m')

# Here, we begin by calling reset(). This ensures that the string with the
# Matlab commands is empty before we start calling different plotting
# commands. After calling contour and quiver, we use the hardcopy command to
# store the plot to a PostScript file. As mentioned above, hardcopy calls
# _replot so there is no need to call show in this case. At the end we call
# save_m to store the Matlab commands in the file mytest2.m. We can then run
# the script as we did above:

os.system("matlab -nojvm -nosplash -r 'mytest2;quit'")

# In this case, we will be brought back to the Python prompt once Matlab
# has stored the plot in the file tmp0.ps.
