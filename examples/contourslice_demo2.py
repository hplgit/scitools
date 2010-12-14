#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-3371.html

from scitools.easyviz import *
from time import sleep
from scipy import io

setp(interactive=False)

mri = io.loadmat('mri_matlab_v6.mat')
D = mri['D']
D = squeeze(D)

image_num = 8

x = xlim;
y = ylim;

# Displaying a 2-D Contour Slice:
contourslice(D,[],[],image_num,indexing='xy')
axis('ij')
xlim(x)
ylim(y)
daspect([1,1,1])
colormap('default')
show()

#hardcopy('tmp_contourslice2a.eps')
#hardcopy('tmp_contourslice2a.png')

figure()
BUG = 1
phandles = contourslice(D,[],[],[1,12,19,27-BUG],8,indexing='xy')
view(3)
axis('tight')
#set(phandles,'LineWidth',2)
setp(phandles, linewidth=4)
show()
#sleep(3)
raw_input('Press Return key to quit: ')

## hardcopy('tmp_contourslice2b.eps')
## hardcopy('tmp_contourslice2b.png')
