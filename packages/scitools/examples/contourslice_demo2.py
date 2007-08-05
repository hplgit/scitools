#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-3371.html

from scitools.easyviz import *
from time import sleep
from scipy import io

mri = io.loadmat('mri_matlab_v6.mat')
D = mri['D']
D = squeeze(D)

image_num = 8

x = xlim;
y = ylim;

# Displaying a 2-D Contour Slice:
setp(show=False)
contourslice(D,[],[],image_num)
axis('ij')
xlim(x)
ylim(y)
daspect([1,1,1])
colormap('default')
camzoom(0.7)  # bug in VTK (camera)

setp(show=True)
show()

#hardcopy('tmp_contourslice3.eps')
#hardcopy('tmp_contourslice3.png')

figure()
BUG = 1
setp(show=False)
phandles = contourslice(D,[],[],[1,12,19,27-BUG],8)
view(3)
axis('tight')
#set(phandles,'LineWidth',2)
setp(phandles, linewidth=4)
setp(show=True)
show()
#sleep(3)
raw_input('press enter')

## hardcopy('tmp_contourslice4.eps')
## hardcopy('tmp_contourslice4.png')
