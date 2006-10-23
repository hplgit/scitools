#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.ch/access/helpdesk/help/techdoc/visualize/f5-3371.html

import os
os.environ['EASYVIZ_BACKEND'] = 'vtk_'

from time import sleep
from scitools.easyviz import *
from scipy import io

mri = io.loadmat('mri_matlab_v6.mat')
D = mri['D']
#D = squeeze(D)

image_num = 8

#x = xlim;
#y = ylim;

# Displaying a 2-D Contour Slice:
set(show=False)
contourslice(D,[],[],image_num)
#axis ij
#xlim(x)
#ylim(y)
daspect([1,1,1])
#colormap('default')

set(show=True)
show()
sleep(3)

BUG = 1
set(show=False)
phandles = contourslice(D,[],[],[1,12,19,27-BUG],8)
view(3)
axis('tight')
#set(phandles,'LineWidth',2)
phandles.set(linewidth=4)
set(show=True)
show()
sleep(3)
