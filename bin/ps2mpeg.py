#!/usr/bin/env python
"""
Turn a set of PostScript files into an MPEG movie.
Each PostScript file becomes a frame in the movie.
mpeg_encode is used to create the MPEG file.
"""

import sys, re, os, glob

if len(sys.argv) < 2:
    print """\
Usage: %s [-nocrop] frame0000.ps frame0001.ps ... [movie.mpeg]
(series of ps files to be included in an MPEG movie movie.mpeg)
""" % sys.argv[0]
    sys.exit(1)

# check that we have mpeg_encode:
from scitools.misc import findprograms
if not findprograms('mpeg_encode'):
    print """
ps2mpeg.py requires the mpeg_encode MPEG encoder program.
Please install mpeg_encode, see URL:
http://bmrc.berkeley.edu/frame/research/mpeg/mpeg_encode.html
"""
    sys.exit(1)
    
# cropping takes time so we can omit that step:
crop = 1
if sys.argv[1] == "-nocrop":
    crop = 0
    del sys.argv[1]

# did the user supply a filename for the MPEG file?
if sys.argv[-1][-3:] != '.ps':
    mpeg_file = sys.argv[-1]
    del sys.argv[-1]
else:
    mpeg_file = "movie.mpeg"

found = findprograms(('gs', 'convert', 'mpeg_encode'), write_message=True)
if not found:
    sys.exit(1)
        
basename = "tmp_";
i = 0  # counter
for psfile in sys.argv[1:]:
    ppmfile = "%s%04d.ppm" % (basename, i)
    gscmd = "gs -q -dBATCH -dNOPAUSE -sDEVICE=ppm "\
            " -sOutputFile=%(ppmfile)s %(psfile)s" % vars()
    print gscmd
    failure = os.system(gscmd)
    if failure:
        print '....gs failed, jumping to next file...'
        continue
    if crop:
        # crop the image:
        tmp_ppmfile = ppmfile + "~"
        os.rename(ppmfile, tmp_ppmfile)
        os.system("convert -crop 0x0 ppm:%s ppm:%s" % \
                  (tmp_ppmfile,ppmfile))
        # using pnmcrop:
        # direct std. error to /dev/null and std. output to file:
        #os.system("pnmcrop %s 2> /dev/null 1> %s" % \
        #          (tmp_ppmfile,ppmfile))
        os.remove(tmp_ppmfile)
    print "%s transformed via gs to %s (%d Kb)" % \
          (psfile,ppmfile,int(os.path.getsize(ppmfile)/1000))
    i = i + 1

first_no = "%04d" % 0                  # first number in ppmfiles
last_no  = "%04d" % (len(sys.argv)-2)  # last  number in ppmfiles
mpeg_encode_file = "%s.mpeg_encode-input" % basename
f = open(mpeg_encode_file, "w")
f.write("""
#
# lines can generally be in any order
# only exception is the option 'INPUT' which must be followed by input
# files in the order in which they must appear, followed by 'END_INPUT'

PATTERN		        I
# more compact files result from the following pattern, but xanim does not
# work well (only a few of the frames are shown):
#PATTERN                 IBBPBBPBBPBBPBB
OUTPUT		        %(mpeg_file)s

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

%(basename)s*.ppm    [%(first_no)s-%(last_no)s]

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
""" % vars())
f.close()
failure = os.system("mpeg_encode " + mpeg_encode_file)
if failure:
    print '\n\nps2mpeg.py: could not make MPEG movie'
else:
    print "mpeg movie in output file", mpeg_file

# remove the generated ppm files:
for file in glob.glob("%s*.ppm" % basename):
    os.remove(file)
#end
