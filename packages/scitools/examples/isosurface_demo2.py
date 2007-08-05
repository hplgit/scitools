#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-3371.html

from scitools.easyviz import *
from time import sleep
from scipy import io

# Displaying an Isosurface:
mri = io.loadmat('mri_matlab_v6.mat')
D = mri['D']
#Ds = smooth3(D);

setp(show=False)
isosurface(D,5)
#hiso = isosurface(Ds,5),
#	'FaceColor',[1,.75,.65],...
#	'EdgeColor','none');
shading('interp')

# Adding an Isocap to Show a Cutaway Surface:
#hcap = patch(isocaps(D,5),...
#	'FaceColor','interp',...
#	'EdgeColor','none');
#colormap(map)

# Define the View:
view(45,30)
axis('tight')
daspect([1,1,.4])

# Add Lighting:
#lightangle(45,30);
#set(gcf,'Renderer','zbuffer'); lighting phong
#isonormals(Ds,hiso)
#set(hcap,'AmbientStrength',.6)
#set(hiso,'SpecularColorReflectance',0,'SpecularExponent',50)

setp(show=True)
show()
#sleep(3)
raw_input('press enter')
#save_script('/tmp/cappediso_script')

#hardcopy('tmp_isosurf3.eps')
#hardcopy('tmp_isosurf3.png')
