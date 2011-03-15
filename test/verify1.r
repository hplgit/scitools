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
MPEG ENCODER STATS (1.5b)
------------------------
TIME STARTED:  Sat Jan 29 08:17:14 2011
MACHINE:  unknown
FIRST FILE:  ./tmp_0000.ppm
LAST FILE:  ./tmp_0012.ppm
PATTERN:  i
GOP_SIZE:  30
SLICES PER FRAME:  1
RANGE:  +/-10
PIXEL SEARCH:  HALF
PSEARCH:  LOGARITHMIC
BSEARCH:  CROSS2
QSCALE:  8 10 25
REFERENCE FRAME:  ORIGINAL


Creating new GOP (closed = T) before frame 0
FRAME 0 (I):  0 seconds  (2990880 bits/s output)
FRAME 1 (I):  0 seconds  (3030000 bits/s output)
FRAME 2 (I):  0 seconds  (3090000 bits/s output)
FRAME 3 (I):  0 seconds  (3149760 bits/s output)
FRAME 4 (I):  0 seconds  (3242400 bits/s output)
FRAME 5 (I):  0 seconds  (3293760 bits/s output)
FRAME 6 (I):  0 seconds  (3337680 bits/s output)
FRAME 7 (I):  0 seconds  (3377280 bits/s output)
FRAME 8 (I):  0 seconds  (3417120 bits/s output)
FRAME 9 (I):  0 seconds  (3412800 bits/s output)
FRAME 10 (I):  0 seconds  (3427680 bits/s output)
FRAME 11 (I):  0 seconds  (3448560 bits/s output)
FRAME 12 (I):  0 seconds  (3448320 bits/s output)


TIME COMPLETED:  Sat Jan 29 08:17:14 2011
Total time:  0 seconds

-------------------------
*****I FRAME SUMMARY*****
-------------------------
  Blocks:    25012     (1420850 bits)     (   56 bpb)
  Frames:       13     (1422208 bits)     (109400 bpf)     (99.9% of total)
  Compression:  108:1     (   0.2221 bpp)
  Seconds:          0     (  21.6667 fps)  ( 10671786 pps)  (    41686 mps)
---------------------------------------------
Total Compression:  107:1     (   0.2223 bpp)
Total Frames Per Second:  Infinite!
CPU Time:  21.666666 fps     (41686 mps)
Total Output Bit Rate (30 fps):  3284086 bits/sec
MPEG file created in :  movie.mpeg


======FRAMES READ:  13
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0000.ppm tmp_0000.eps
tmp_0000.eps transformed via gs to tmp_0000.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0001.ppm tmp_0001.eps
tmp_0001.eps transformed via gs to tmp_0001.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0002.ppm tmp_0002.eps
tmp_0002.eps transformed via gs to tmp_0002.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0003.ppm tmp_0003.eps
tmp_0003.eps transformed via gs to tmp_0003.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0004.ppm tmp_0004.eps
tmp_0004.eps transformed via gs to tmp_0004.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0005.ppm tmp_0005.eps
tmp_0005.eps transformed via gs to tmp_0005.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0006.ppm tmp_0006.eps
tmp_0006.eps transformed via gs to tmp_0006.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0007.ppm tmp_0007.eps
tmp_0007.eps transformed via gs to tmp_0007.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0008.ppm tmp_0008.eps
tmp_0008.eps transformed via gs to tmp_0008.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0009.ppm tmp_0009.eps
tmp_0009.eps transformed via gs to tmp_0009.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0010.ppm tmp_0010.eps
tmp_0010.eps transformed via gs to tmp_0010.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0011.ppm tmp_0011.eps
tmp_0011.eps transformed via gs to tmp_0011.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0012.ppm tmp_0012.eps
tmp_0012.eps transformed via gs to tmp_0012.ppm (1503 Kb)
ps2mpeg made the following ppm files:
tmp_0007.ppm
tmp_0008.ppm
tmp_0009.ppm
tmp_0000.ppm
tmp_0003.ppm
tmp_0005.ppm
tmp_0011.ppm
tmp_0001.ppm
tmp_0010.ppm
tmp_0012.ppm
tmp_0002.ppm
tmp_0004.ppm
tmp_0006.ppm
mpeg movie in output file movie.mpeg

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
         70037 function calls in 0.828 CPU seconds

 internal time

lineno(function)
26(isfile)
7(f1)
38(isdir)
40(S_ISDIR)
12(f2)
24(S_IFMT)
1(<module>)
2(<module>)
0(profiler)



test of subst in the following file:
# some comment
def f(x):
    return 2

compute_formula1(x, y, z)
if not first:
    compute_formula2(a, b)
compute_(.+?)\( replaced by calculate_\g<1>( in tmp1.py
after substitution:
# some comment
def f(x):
    return 2

calculate_formula1(x, y, z)
if not first:
    calculate_formula2(a, b)

test of rename:
files:
tmp_bergen_set21555.dat
tmp_oslo_set30490.dat
tmp_stavanger_set7482.dat
tmp_trondheim_set2859.dat
rename: change name from (e.g.) tmp_oslo_set143 set_143_oslo.dat
tmp_bergen_set21555.dat renamed to set_21555_bergen.dat
tmp_oslo_set30490.dat renamed to set_30490_oslo.dat
tmp_stavanger_set7482.dat renamed to set_7482_stavanger.dat
tmp_trondheim_set2859.dat renamed to set_2859_trondheim.dat
new names:
set_21555_bergen.dat
set_2859_trondheim.dat
set_30490_oslo.dat
set_7482_stavanger.dat
copies of old files:
tmp_0000.eps
tmp_0001.eps
tmp_0002.eps
tmp_0003.eps
tmp_0004.eps
tmp_0005.eps
tmp_0006.eps
tmp_0007.eps
tmp_0008.eps
tmp_0009.eps
tmp_0010.eps
tmp_0011.eps
tmp_0012.eps
tmp_bergen_set21555.dat.old~~
tmp_.mpeg_encode-input
tmp_oslo_set30490.dat.old~~
tmp_stavanger_set7482.dat.old~~
tmp_trondheim_set2859.dat.old~~
set_21555_bergen.dat renamed to set_21555_bergen.data
set_2859_trondheim.dat renamed to set_2859_trondheim.data
set_30490_oslo.dat renamed to set_30490_oslo.data
set_7482_stavanger.dat renamed to set_7482_stavanger.data
set_21555_bergen.data
set_2859_trondheim.data
set_30490_oslo.data
set_7482_stavanger.data

test of file2interactive:
>>> import os
>>> origdir = os.getcwd()
>>> os.chdir(os.pardir)
>>> os.getcwd()
'/home/hpl/vc/scitools'
>>> origdir
'/home/hpl/vc/scitools/test'
>>> 
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
MPEG ENCODER STATS (1.5b)
------------------------
TIME STARTED:  Sat Jan 29 08:22:16 2011
MACHINE:  unknown
FIRST FILE:  ./tmp_0000.ppm
LAST FILE:  ./tmp_0012.ppm
PATTERN:  i
GOP_SIZE:  30
SLICES PER FRAME:  1
RANGE:  +/-10
PIXEL SEARCH:  HALF
PSEARCH:  LOGARITHMIC
BSEARCH:  CROSS2
QSCALE:  8 10 25
REFERENCE FRAME:  ORIGINAL


Creating new GOP (closed = T) before frame 0
FRAME 0 (I):  0 seconds  (2990880 bits/s output)
FRAME 1 (I):  0 seconds  (3030000 bits/s output)
FRAME 2 (I):  0 seconds  (3090000 bits/s output)
FRAME 3 (I):  0 seconds  (3149760 bits/s output)
FRAME 4 (I):  0 seconds  (3242400 bits/s output)
FRAME 5 (I):  0 seconds  (3293760 bits/s output)
FRAME 6 (I):  0 seconds  (3337680 bits/s output)
FRAME 7 (I):  0 seconds  (3377280 bits/s output)
FRAME 8 (I):  0 seconds  (3417120 bits/s output)
FRAME 9 (I):  0 seconds  (3412800 bits/s output)
FRAME 10 (I):  0 seconds  (3427680 bits/s output)
FRAME 11 (I):  0 seconds  (3448560 bits/s output)
FRAME 12 (I):  0 seconds  (3448320 bits/s output)


TIME COMPLETED:  Sat Jan 29 08:22:17 2011
Total time:  1 seconds

-------------------------
*****I FRAME SUMMARY*****
-------------------------
  Blocks:    25012     (1420850 bits)     (   56 bpb)
  Frames:       13     (1422208 bits)     (109400 bpf)     (99.9% of total)
  Compression:  108:1     (   0.2221 bpp)
  Seconds:          0     (  19.5000 fps)  (  9604608 pps)  (    37518 mps)
---------------------------------------------
Total Compression:  107:1     (   0.2223 bpp)
Total Frames Per Second:  13.000000 (25012 mps)
CPU Time:  19.499999 fps     (37517 mps)
Total Output Bit Rate (30 fps):  3284086 bits/sec
MPEG file created in :  movie.mpeg


======FRAMES READ:  13
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0000.ppm tmp_0000.eps
tmp_0000.eps transformed via gs to tmp_0000.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0001.ppm tmp_0001.eps
tmp_0001.eps transformed via gs to tmp_0001.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0002.ppm tmp_0002.eps
tmp_0002.eps transformed via gs to tmp_0002.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0003.ppm tmp_0003.eps
tmp_0003.eps transformed via gs to tmp_0003.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0004.ppm tmp_0004.eps
tmp_0004.eps transformed via gs to tmp_0004.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0005.ppm tmp_0005.eps
tmp_0005.eps transformed via gs to tmp_0005.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0006.ppm tmp_0006.eps
tmp_0006.eps transformed via gs to tmp_0006.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0007.ppm tmp_0007.eps
tmp_0007.eps transformed via gs to tmp_0007.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0008.ppm tmp_0008.eps
tmp_0008.eps transformed via gs to tmp_0008.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0009.ppm tmp_0009.eps
tmp_0009.eps transformed via gs to tmp_0009.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0010.ppm tmp_0010.eps
tmp_0010.eps transformed via gs to tmp_0010.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0011.ppm tmp_0011.eps
tmp_0011.eps transformed via gs to tmp_0011.ppm (1503 Kb)
gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm  -sOutputFile=tmp_0012.ppm tmp_0012.eps
tmp_0012.eps transformed via gs to tmp_0012.ppm (1503 Kb)
ps2mpeg made the following ppm files:
tmp_0007.ppm
tmp_0008.ppm
tmp_0009.ppm
tmp_0000.ppm
tmp_0003.ppm
tmp_0005.ppm
tmp_0011.ppm
tmp_0001.ppm
tmp_0010.ppm
tmp_0012.ppm
tmp_0002.ppm
tmp_0004.ppm
tmp_0006.ppm
mpeg movie in output file movie.mpeg

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
         70037 function calls in 0.802 CPU seconds

 internal time

lineno(function)
26(isfile)
7(f1)
38(isdir)
40(S_ISDIR)
12(f2)
24(S_IFMT)
1(<module>)
2(<module>)
0(profiler)



test of subst in the following file:
# some comment
def f(x):
    return 2

compute_formula1(x, y, z)
if not first:
    compute_formula2(a, b)
compute_(.+?)\( replaced by calculate_\g<1>( in tmp1.py
after substitution:
# some comment
def f(x):
    return 2

calculate_formula1(x, y, z)
if not first:
    calculate_formula2(a, b)

test of rename:
files:
tmp_bergen_set11481.dat
tmp_oslo_set16807.dat
tmp_stavanger_set3114.dat
tmp_trondheim_set15089.dat
rename: change name from (e.g.) tmp_oslo_set143 set_143_oslo.dat
tmp_bergen_set11481.dat renamed to set_11481_bergen.dat
tmp_oslo_set16807.dat renamed to set_16807_oslo.dat
tmp_stavanger_set3114.dat renamed to set_3114_stavanger.dat
tmp_trondheim_set15089.dat renamed to set_15089_trondheim.dat
new names:
set_11481_bergen.dat
set_15089_trondheim.dat
set_16807_oslo.dat
set_3114_stavanger.dat
copies of old files:
tmp_0000.eps
tmp_0001.eps
tmp_0002.eps
tmp_0003.eps
tmp_0004.eps
tmp_0005.eps
tmp_0006.eps
tmp_0007.eps
tmp_0008.eps
tmp_0009.eps
tmp_0010.eps
tmp_0011.eps
tmp_0012.eps
tmp_bergen_set11481.dat.old~~
tmp_.mpeg_encode-input
tmp_oslo_set16807.dat.old~~
tmp_stavanger_set3114.dat.old~~
tmp_trondheim_set15089.dat.old~~
set_11481_bergen.dat renamed to set_11481_bergen.data
set_15089_trondheim.dat renamed to set_15089_trondheim.data
set_16807_oslo.dat renamed to set_16807_oslo.data
set_3114_stavanger.dat renamed to set_3114_stavanger.data
set_11481_bergen.data
set_15089_trondheim.data
set_16807_oslo.data
set_3114_stavanger.data

test of file2interactive:
>>> import os
>>> origdir = os.getcwd()
>>> os.chdir(os.pardir)
>>> os.getcwd()
'/home/hpl/vc/scitools'
>>> origdir
'/home/hpl/vc/scitools/test'
>>> 
