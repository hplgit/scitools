#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.ch/access/helpdesk/help/techdoc/visualize/f5-3371.html

import os
os.environ['EASYVIZ_BACKEND'] = 'vtk_'

from time import sleep
from scitools.easyviz import *
from scipy import io

# Displaying an Isosurface:
mri = io.loadmat('mri_matlab_v6.mat')
D = mri['D']
#Ds = smooth3(D);

set(show=False)
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
#view(45,30)
view(3)
axis('tight')
daspect([1,1,.4])

# Add Lighting:
#lightangle(45,30);
#set(gcf,'Renderer','zbuffer'); lighting phong
#isonormals(Ds,hiso)
#set(hcap,'AmbientStrength',.6)
#set(hiso,'SpecularColorReflectance',0,'SpecularExponent',50)

set(show=True)
show()
sleep(3)
