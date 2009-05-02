<HTML><BODY>
<P><A NAME="part1"><B>/home/hpl/vc/scitools/test: test1.r test1.v   16 lines differ</B></A><BR>The differences were calculated by diff .<PRE>
18c18
< 0.136695425446
---
> 0.136695425435
30c30
< 0.733446956224
---
> 0.733435956224
32c32
< 0.733446956224
---
> 0.733435956224
44c44
< 0.136695425446
---
> 0.136695425435

</PRE>
<P><A HREF="/home/hpl/vc/scitools/test/tmp.test1_fdiff.sh">Floating-point difference between test1.vd and test1.rd without any approximations</A>

</BODY></HTML>

#
# lines can generally be in any order
# only exception is the option 'INPUT' which must be followed by input
# files in the order in which they must appear, followed by 'END_INPUT'

PATTERN		        I
# more compact files result from the following pattern, but xanim does not
# work well (only a few of the frames are shown):
#PATTERN                 IBBPBBPBBPBBPBB
OUTPUT		        movie.mpeg

# mpeg_encode really only accepts 3 different file formats, but using a
# conversion statement it can effectively handle ANY file format
#
# you must specify whether you will convert to PNM or PPM or YUV format

BASE_FILE_FORMAT	PPM

# the conversion statement
#
# Each occurrence of '*' will be replaced by the input file
#
# e.g., if you have a bunch of GIF files, then this might be:
#	INPUT_CONVERT	giftoppm *
#
# if you have a bunch of files like a.Y a.U a.V, etc., then:
#	INPUT_CONVERT	cat *.Y *.U *.V
#
# if you are grabbing from laser disc you might have something like
#	INPUT_CONVERT	goto frame *; grabppm
# 'INPUT_CONVERT *' means the files are already in the base file format
#
INPUT_CONVERT	*

# number of frames in a GOP.
#
# since each GOP must have at least one I-frame, the encoder will find the
# the first I-frame after GOP_SIZE frames to start the next GOP
#
# later, will add more flexible GOP signalling
#
GOP_SIZE	30
#GOP_SIZE	6

# number of slices in a frame
#
# 1 is a good number.  another possibility is the number of macroblock rows
# (which is the height divided by 16)
#
SLICES_PER_FRAME	1

# directory to get all input files from (makes this file easier to read)
INPUT_DIR	.

INPUT
# '*' is replaced by the numbers 01, 02, 03, 04
# if I instead do [01-11], it would be 01, 02, ..., 09, 10, 11
# if I instead do [1-11], it would be 1, 2, 3, ..., 9, 10, 11
# if I instead do [1-11+3], it would be 1, 4, 7, 10
# the program assumes none of your input files has a name ending in ']'
# if you do, too bad!!!
#
#

tmp_*.ppm    [0000-0012]

# can have more files here if you want...there is no limit on the number
# of files
END_INPUT

# all of the remaining options have to do with the motion search and qscale
# FULL or HALF -- must be upper case
PIXEL		HALF
# means +/- this many pixels
RANGE		10
# this must be one of {EXHAUSTIVE, SUBSAMPLE, LOGARITHMIC}
PSEARCH_ALG	LOGARITHMIC
# this must be one of {SIMPLE, CROSS2, EXHAUSTIVE}
#
# note that EXHAUSTIVE is really, really, really slow
#
BSEARCH_ALG	CROSS2
#
# these specify the q-scale for I, P, and B frames
# (values must be between 1 and 31)
#
IQSCALE		8
PQSCALE		10
BQSCALE		25

# this must be ORIGINAL or DECODED
REFERENCE_FRAME	ORIGINAL
56 2009    .tmp.profile

         120056 function calls in 1.852 CPU seconds

 internal time

lineno(function)
0(stat)
26(isfile)
7(f1)
38(isdir)
40(S_ISDIR)
12(f2)
24(S_IFMT)
0(execfile('cpu.py'))
0(setprofile)
0(execfile)
2(<module>)
0(range)
0(profiler)
1(<module>)


>>> import sys, os
>>> sys.prefix
'/home/hpl/sysdir/Linux'
>>> sys.argv
['/home/hpl/vc/scitools/bin/scitools', 'file2interactive', 'tmp.2']
>>> os.pardir
'..'
>>> os.curdir
'.'
>>> 
