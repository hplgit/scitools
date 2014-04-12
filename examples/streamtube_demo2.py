#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-6736.html

from scitools.easyviz import *
from scipy import io

wind = io.loadmat('wind_matlab_v6.mat')
x = wind['x']
y = wind['y']
z = wind['z']
u = wind['u']
v = wind['v']
w = wind['w']

xmin = arrmin(x)
xmax = arrmax(x)
ymin = arrmin(y)
alt = 7.356 # z-value for slice and streamtube plane
wind_speed = sqrt(u**2 + v**2 + w**2)

setp(interactive=False)

# Draw Slice Planes:
hslice = slice_(x,y,z,wind_speed,xmax,ymin,alt)
hold('on')
#set(hslice,'FaceColor','interp','EdgeColor','none')
ax = gca()
ax.setp(shading='interp')
colormap(hsv(16))

# Add Contour Lines to Slice Planes:
#color_lim = caxis()
# BUG: caxis() returns [None,None]
color_lim = [0.2681,78.9072] 
cont_intervals = linspace(color_lim[0],color_lim[1],17)
hcont = contourslice(x,y,z,wind_speed,xmax,ymin,alt,cont_intervals.tolist())
# BUG: In Volume._parseargs_slice_ in common.py line 932:
#                 elif isinstance(tmparg, (list,tuple)):
# should also accept NumPy arrays!

#set(hcont,'EdgeColor',[.4 .4 .4],'LineWidth',1)
hcont.setp(linewidth=2)

# Create the Stream Tubes:
sx,sy,sz = ndgrid([xmin]*11,seq(20,50,3),[alt]*11)
daspect([1,1,1]) # set DAR before calling streamtube
htubes = streamtube(x,y,z,u,v,w,sx,sy,sz)#,[1.25, 5])
#set(htubes,'EdgeColor','none','FaceColor','r','AmbientStrength',.5)

# Define the view:
view(-100,30)
#axis(volumebounds(x,y,z,wind_speed))
#set(gca,'Projection','perspective')
ax.setp(projection='perspective')
#camlight left
grid('off')

show()

raw_input('Press Return key to quit: ')

#hardcopy('tmp_streamtube2.eps')
#hardcopy('tmp_streamtube2_lq.eps', vector_file=False)
#hardcopy('tmp_streamtube2.png')



