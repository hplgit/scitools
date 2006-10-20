#!/usr/bin/env python

"""
Known issues:

- .jpg images created by the Vtk backend dosen't seem to work with the
  mencoder and ffmpeg tools. This can be fixed by setting the force_conversion
  argument to True. This will force conversion of the .jpg files to .png files
  which in turn should successfully create the movie.

- apsect ratio in mpeg_encode doesn't seem to work.
"""

import os, glob, re

from scitools.misc import findprograms
from misc import _check_type

class MovieEncoder(object):
    _local_prop = {
        'input_files': None, 
        'output_file': None, 
        'overwrite_output': False,   # overwrite output file if true
        'encoder': None,             # default encoding tool
        'vbitrate': 800,             # default video bit rate
        'vbuffer': None,             # video buffer
        'fps': 25,                   # default frame rate
        'vcodec': 'mpeg4',           # default video codec
        'size': None,
        'quiet': False,
        'aspect': None,
        'prefered_package': 'ImageMagick',
        'qscale': None,
        'qmin': 2,
        'qmax': 31,
        'iqscale': None,
        'pqscale': None,
        'bqscale': None,
        'pattern': 'I',
        'gop_size': None,
        'force_conversion': False,
        }
    _legal_encoders = 'mencoder ffmpeg mpeg_encode ppmtompeg mpeg2enc'.split()
    _legal_file_types = 'png gif jpg ps eps bmp tif tga pnm'.split()

    def __init__(self, input_files, **kwargs):
        self._prop = {}
        self._prop.update(self._local_prop)
        self._prop['input_files'] = input_files
        for key in kwargs:
            if key in self._prop:
                self._prop[key] = kwargs[key]

        # determine which encoder to be used:
        encoder = self._prop['encoder']
        if encoder is None:
            for enc in self._legal_encoders:
                if findprograms(enc):
                    encoder = enc
                    break
            if encoder is None:
                raise Exception, "None of the supported encoders is installed"
            self._prop['encoder'] = encoder
        else:
            if not encoder in self._legal_encoders:
                raise ValueError, "encoder must be %s, not %s" % \
                      (self._legal_encoders, encoder)
            if not findprograms(encoder):
                raise Exception, "The selected encoder (%s) is not installed" \
                      % encoder

        # determine the file type of the input files:
        if isinstance(input_files, (tuple,list)):
            file_ = input_files[0]
        elif isinstance(input_files, str):
            file_ = input_files
        else:
            raise ValueError, "The input files must be given as either a "\
                  "list/tuple of strings or a string, not %s" % \
                  type(input_files)
        fname, ext = os.path.splitext(file_)
        if not ext:
            raise ValueError, "Unable to determine file type from file name."
        file_type = ext[1:] # remove the . (dot)
        if not file_type in self._legal_file_types:
            raise TypeError, "file type must be %s, not '%s'" % \
                  (self._legal_file_types, file_type)
        self._prop['file_type'] = file_type
        
    def encode(self):
        """Encode a series of images to a movie."""
        # check that the selected encoder is legal:
        encoder = self._prop['encoder']
        if not encoder in self._legal_encoders:
            raise ValueError, "encoder must be one of %s, not '%s'" % \
                  (self._legal_encoders, encoder)

        # get command string:
        exec('cmd=self._%s()' % encoder)

        # run command:
        if not self._prop['quiet']:
            print "Running: \n\n%s\n" % cmd
        failure = os.system(cmd)
        if failure:
            print '\n\ncould not make movie'
        elif not self._prop['quiet']:
            print "\n\nmovie in output file", self._prop['output_file']

        # clean up temporary files:
        if hasattr(self, '_tmp_files'): 
            for tmp_file in self._tmp_files:
                os.remove(tmp_file)

    def _mencoder(self):
        """Create a string with commands for creating a movie with the
        mencoder encoding program.
        """
        encoder = self._prop['encoder']
        cmd = encoder
        file_type = self._prop['file_type']
        files = self._prop['input_files']
        if isinstance(files, str):
            pattern = r'(.*)%(\d+)d(.*\..*)'
            match = re.search(pattern, files)
            if match:
                pre = match.group(1)
                num = int(match.group(2))
                ext = match.group(3)
                files = pre + '[0-9]'*num + ext
            files = glob.glob(files)
            if not files:
                raise ValueError, \
                      "%s is not a valid file specification or the files "\
                      "doesn't exist." % self._prop['input_files']
        if isinstance(files, (list,tuple)):
            if not file_type in ['jpg', 'png'] or \
                   self._prop['force_conversion']:
                # since mencoder only supports jpg and png files, we have to
                # create copies of the input files and convert them to jpg.
                files = self._any2any(files, ofile_ext='.png')
                file_type = 'png'
                self._tmp_files = files[:] # store files for later removal
            # give the files as a comma separated string to mencoder:
            files = ','.join(files)
        cmd += ' "mf://%s" -mf' % files
        cmd += ' fps=%g' % float(self._prop['fps'])
        cmd += ':type=%s' % file_type
        vbitrate = self._prop['vbitrate']
        vcodec = self._prop['vcodec']
        qscale = self._prop['qscale']
        qmin = self._prop['qmin']
        qmax = self._prop['qmax']
        vbuffer = self._prop['vbuffer']
        if vcodec == 'xvid':
            cmd += ' -ovc xvid -xvidencopts'
            if qscale is not None:
                cmd += ' fixed_quant=%s' % qscale
            else:
                cmd += ' bitrate=%s:' % vbitrate
                cmd += 'min_iquant=%s:max_iquant=%s:' % (qmin, qmax)
                cmd += 'min_pquant=%s:max_pquant=%s:' % (qmin, qmax)
                cmd += 'min_bquant=%s:max_bquant=%s' % (qmin, qmax)
        else:
            # mbd: macroblock decision
            cmd += ' -ovc lavc -lavcopts vcodec=%s:mbd=1' % vcodec
            if vbitrate is not None:
                cmd += ':vbitrate=%s' % vbitrate
                #cmd += ':vrc_minrate=%s:vrc_maxrate=%s' % ((vbitrate,)*2)
            if qscale is not None:
                cmd += ':vqscale=%s' % qscale
            else:
                cmd += ':vqmin=%s:vqmax=%s' % (qmin, qmax)
            if vbuffer is not None:
                cmd += ':vrc_buf_size=%s' % vbuffer
        aspect = self._prop['aspect']
        if aspect is not None:
            cmd += ':aspect=%s' % aspect
        #cmd += ' -oac copy' # audio
        size = self._get_size()
        if size is not None:
            cmd += ' -vf scale=%s:%s' % (size[0], size[1])
        # if no output file is given, use 'movie.avi' as default:
        if self._prop['output_file'] is None: 
            self._prop['output_file'] = 'movie.avi'
        output_file = self._prop['output_file']
        if os.path.isfile(output_file) and not self._prop['overwrite_output']:
            raise Exception, \
                  "Output file %s already exist. Use 'overwrite_output=True'" \
                  " to overwrite the file." % output_file
        cmd += ' -o %s' % output_file
        if self._prop['quiet']:
            cmd += ' > /dev/null 2>&1'
        return cmd

    def _ffmpeg(self):
        """Create and return a string with commands for making a movie with the
        FFmpeg tool.
        """
        encoder = self._prop['encoder']
        cmd = encoder
        files = self._prop['input_files']
        file_type = self._prop['file_type']
        if isinstance(files, str):
            pattern = r'(.*)%(\d+)d(.*\..*)'
            match = re.search(pattern, files)
            if match:
                if file_type not in ['jpg', 'png'] or \
                       self._prop['force_conversion']:
                    pre = match.group(1)
                    num = int(match.group(2))
                    ext = match.group(3)
                    files = pre + '[0-9]'*num + ext
                    files = glob.glob(files)
            else:
                files = glob.glob(files)
        if isinstance(files, (list,tuple)):
            basename = 'tmp_'
            files = self._any2any(files, basename=basename, ofile_ext='.png')
            file_type = 'png'
            self._tmp_files = files[:]
            # create a new string with the right pattern:
            files = basename + '%04d.png'
        cmd += ' -i "%s"' % files
        cmd += ' -b %s' % self._prop['vbitrate']
        cmd += ' -r %s' % self._prop['fps']
        size = self._get_size()
        if size is not None:
            cmd += ' -s %sx%s' % size
        if self._prop['vcodec'] is not None:
            cmd += ' -vcodec %s' % self._prop['vcodec']
        if self._prop['overwrite_output']:
            cmd += ' -y'
        if self._prop['aspect'] is not None:
            cmd += ' -aspect %s' % self._prop['aspect']
        if self._prop['qscale'] is not None:
            cmd += ' -qscale %s' % self._prop['qscale']
        else:
            cmd += ' -qmin %s -qmax %s' % \
                   (self._prop['qmin'], self._prop['qmax'])
        if self._prop['vbuffer'] is not None:
            cmd += ' -bufsize %s' % self._prop['vbuffer']
        if self._prop['gop_size'] is not None:
            cmd += ' -g %d' % int(self._prop['gop_size'])
        #cmd += ' -target dvd'
        # if no output file is given, use 'movie.avi' as default:
        if self._prop['output_file'] is None: 
            self._prop['output_file'] = 'movie.avi'
        cmd += ' ' + self._prop['output_file']
        if self._prop['quiet']:
            cmd += ' > /dev/null 2>&1'
        return cmd

    def _mpeg_encode(self):
        """Create and return a string with commands for creating a movie with
        the mpeg_encode tool.
        """
        encoder = self._prop['encoder']
        basename = 'tmp_'  # basename for temporary files

        # set frame rate:
        # mpeg_encode only supports a given set of frame rates:
        legal_frame_rates = (23.976, 24, 25, 29.97, 30, 50 ,59.94, 60)
        if self._prop['fps'] in legal_frame_rates:
            fps = self._prop['fps']
        else:
            raise ValueError, \
                  "%s only supports the following frame rates: %s" % \
                  (encoder, legal_frame_rates)

        # set aspect ratio:
        legal_aspects = (1.0, 0.6735, 0.7031, 0.7615, 0.8055,
                         0.8437, 0.8935, 0.9157, 0.9815, 1.0255,
                         1.0695, 1.0950, 1.1575, 1.2015)
        aspect = self._prop['aspect']
        if aspect is not None:
            if aspect not in legal_aspects:
                raise ValueError, \
                      "%s only supports the following aspect ratios: %s" % \
                      (encoder, legal_aspects)
        else:
            aspect = 1.0
        print aspect

        # get image files:
        files = self._prop['input_files']
        if isinstance(files, str):
            pattern = r'(.*)%(\d+)d(.*\..*)'
            match = re.search(pattern, files)
            if match:
                pre = match.group(1)
                num = int(match.group(2))
                ext = match.group(3)
                files = pre + '[0-9]'*num + ext
            files = glob.glob(files)
        if not files:
            raise ValueError, \
                  "%s is not a valid file specification or the files " \
                  "doesn't exist." % files
        size = self._get_size()
        if size is not None or self._prop['file_type'] != 'pnm' or \
               self._prop['force_conversion']:
            files = self._any2any(files, basename=basename, size=size)
            self._tmp_files = files[:]
        files = '\n'.join(files)

        # set input dir:
        input_dir = os.path.split(files[0])[0]
        if input_dir == '':
            input_dir = '.'

        # set output file:
        if self._prop['output_file'] is None:
            self._prop['output_file'] = 'movie.mpeg'
        mpeg_file = self._prop['output_file']
        if os.path.isfile(mpeg_file) and not self._prop['overwrite_output']:
            raise Exception, \
                  "Output file %s already exist. Use 'overwrite_output=True'" \
                  " to overwrite the file." % mpeg_file

        # set pattern (sequence of I, P, and B frames):
        pattern = self._prop['pattern']
        if isinstance(pattern, str):
            pattern = pattern.upper()  # pattern must be uppercase
        else:
            # give warning?
            pattern = 'I'

        # set quantization scale for I, P, and B frames:
        qscale = self._prop['qscale']
        iqscale = self._prop['iqscale']
        pqscale = self._prop['pqscale']
        bqscale = self._prop['bqscale']
        if qscale is not None:
            if iqscale is None: iqscale = qscale
            if pqscale is None: pqscale = qscale
            if bqscale is None: bqscale = qscale
        else:
            if iqscale is None: iqscale = 8
            if pqscale is None: pqscale = 10
            if bqscale is None: bqscale = 25

        # set gop size:
        gop_size = self._prop['gop_size']
        if gop_size is not None:
            gop_size = int(gop_size)
        else:
            gop_size = 15

        # create an mpeg_encode parameter file:
        mpeg_encode_file = "%s.mpeg_encode-input" % basename
        f = open(mpeg_encode_file, "w")
        f.write("""
PATTERN	         %(pattern)s
OUTPUT           %(mpeg_file)s
BASE_FILE_FORMAT PNM
INPUT_CONVERT    *
GOP_SIZE         %(gop_size)d
#GOP_SIZE         16
SLICES_PER_FRAME 1
INPUT_DIR        %(input_dir)s
INPUT
%(files)s
END_INPUT
PIXEL            FULL
#PIXEL            HALF
RANGE            10
PSEARCH_ALG      LOGARITHMIC
BSEARCH_ALG      CROSS2
IQSCALE	         %(iqscale)d
PQSCALE	         %(pqscale)d
BQSCALE	         %(bqscale)d
REFERENCE_FRAME  ORIGINAL
FRAME_RATE       %(fps)d
ASPECT_RATIO     %(aspect)s
FORCE_ENCODE_LAST_FRAME
""" % vars())
        
        # set video bit rate and buffer size:
        vbitrate = self._prop['vbitrate']
        if isinstance(vbitrate, (float,int)):
            f.write("BIT_RATE         %d" % (int(vbitrate)*1000))
        vbuffer = self._prop['vbuffer']
        if isinstance(vbuffer, (float,int)):
            f.write("BUFFER_SIZE      %d" % (int(vbuffer)*1000))
        f.close()
        
        if not hasattr(self, '_tmp_files'):
            self._tmp_files = []
        self._tmp_files.append(mpeg_encode_file)

        # create the command string:
        cmd = encoder
        if self._prop['quiet']:
            cmd += ' -realquiet'
        cmd += ' ' + mpeg_encode_file
        return cmd

    # mpeg_encode and ppmtompeg is the same encoding tool:
    _ppmtompeg = _mpeg_encode

    def _mpeg2enc(self):
        """Create and return a string with commands for making a movie with
        the mpeg2enc tool (from MJPEGTools).
        """
        encoder = self._prop['encoder']
        png2yuv = 'png2yuv'
        jpeg2yuv = 'jpeg2yuv'
        yuvscaler = 'yuvscaler'
        
        file_type = self._prop['file_type']
        files = self._prop['input_files']
        if isinstance(files, str):
            pattern = r'(.*)%(\d+)d(.*\..*)'
            match = re.search(pattern, files)
            if match:
                if file_type not in ['jpg', 'png'] or \
                       self._prop['force_conversion']:
                    pre = match.group(1)
                    num = int(match.group(2))
                    ext = match.group(3)
                    files = pre + '[0-9]'*num + ext
                    files = glob.glob(files)
            else:
                files = glob.glob(files)
        if isinstance(files, (list,tuple)):
            basename = 'tmp_'
            files = self._any2any(files, basename=basename, ofile_ext='.png')
            file_type = 'png'
            self._tmp_files = files[:]
            # create a new string with the right pattern:
            files = basename + '%04d.png'
            
        cmd = ''
        if file_type == 'jpg' and findprograms(jpeg2yuv):
            cmd += jpeg2yuv
        elif findprograms(png2yuv):
            cmd += png2yuv
        else:
            raise Exception, "png2yuv or jpeg2yuv is not installed"
        cmd += ' -f 25' # frame rate
        cmd += ' -I p'  # interlacing mode: p = none / progressive
        cmd += ' -j "%s"' % files # set image files
        # find start image:
        for i in xrange(9999):
            if os.path.isfile(files % i):
                cmd += ' -b %d' % i
                break
        if self._prop['quiet']:
            cmd += ' -v 0' # verbosity level 0

        # set size of movie (by using the yuvscaler tool):
        size = self._get_size()
        if size is not None and findprograms(yuvscaler):
            width, height = size
            cmd += ' | %(yuvscaler)s -O SIZE_%(width)sx%(height)s' % vars()

        # if no output file is given, use 'movie.avi' as default:
        if self._prop['output_file'] is None: 
            self._prop['output_file'] = 'movie.mpeg'
        output_file = self._prop['output_file']
        if os.path.isfile(output_file) and not self._prop['overwrite_output']:
            raise Exception, \
                  "Output file %s already exist. Use 'overwrite_output=True'" \
                  " to overwrite the file." % output_file

        cmd += ' | '
        cmd += encoder
        if self._prop['vcodec'] == 'mpeg2video':
            cmd += ' -f 3' # generic mpeg-2 video
        else:
            cmd += ' -f 0' # generic mpeg-1 video
        if self._prop['vbitrate'] is not None:
            cmd += ' -b %d' % int(self._prop['vbitrate'])
        if self._prop['vbuffer'] is not None:
            cmd += ' -V %d' % int(self._prop['vbuffer'])
        if self._prop['qscale'] is not None:
            cmd += ' -q %s' % self._prop['qscale']

        # set movie frame rate:
        legal_fps = {'23.976': 1, '24': 2, '25': 3, '29.97': 4,
                     '30': 5, '50': 6, '59.94': 7, '60': 8}
        fps = str(self._prop['fps'])
        if not fps in legal_fps:
            raise ValueError, "fps must be %s, not %s" % \
                  (fps_convert.keys(), fps)
        cmd += ' -F %s' % legal_fps[fps]
        #cmd += ' --cbr' # constant bit rate
        gop_size = self._prop['gop_size']
        if gop_size is not None:
            # set min (-g) and max (-G) gop size to the same value:
            cmd += ' -g %s -G %s' % (gop_size, gop_size)

        # set aspect ratio:
        legal_aspects = {'1.0': 1, '1.3': 2, '1.7': 3, '2.21': 4}
        aspect = self._get_aspect_ratio()
        if aspect is not None:
            if aspect not in legal_aspects.values():
                aspect = str(aspect)
                for key in legal_aspects.keys():
                    if aspect.startswith(key):
                        aspect = legal_aspects[key]
                        break
                if aspect not in legal_aspects.values():
                    raise ValueError, \
                          "aspect must be either 1:1, 4:3, 16:9, or 2.21:1," \
                          " not %s" % aspect
            cmd += ' -a %s' % aspect

        # set output file:
        cmd += ' -o %s' % self._prop['output_file']
        if self._prop['quiet']:
            cmd += ' -v 0' # verbosity level 0 (warnings and errors only)
        return cmd

    def _any2any(self, files, basename='tmp_', size=None, ofile_ext='.pnm'):
        # Converts a list of files to the file format specified in the
        # ofile_ext keyword argument. Using either Netpbm tools or convert
        # (from the ImageMagick package).
        netpbm_converters = {'.png': ('pngtopnm', 'pnmtopng'),
                             '.gif': ('giftopnm',  'ppmtogif'),
                             '.jpg': ('jpegtopnm', 'pnmtojpeg'),
                             '.ps':  ('pstopnm', 'pnmtops'),
                             '.eps': ('pstopnm', 'pnmtops'),
                             '.bmp': ('bmptopnm', 'ppmtobmp'),
                             '.tif': ('tifftopnm', 'pnmtotiff'),
                             '.tga': ('tgatopnm', 'ppmtotga'),
                             '.pnm': ('cat', ''),
                             }
        _check_type(files, 'files', (list,tuple))
        ifile_ext = os.path.splitext(files[0])[1]
        anytopnm = netpbm_converters[ifile_ext][0]
        pnmtoany = netpbm_converters[ofile_ext][1]
        pnmscale = 'pnmscale'
        #pnmcrop = 'pnmcrop'
        convert = 'convert'
        
        app = anytopnm
        if findprograms((convert, anytopnm, pnmtoany)):
            if self._prop['prefered_package'].lower() == 'imagemagick':
                app = convert
        elif findprograms(convert):
            app = convert
        elif not findprograms((anytopnm, pnmtoany)):
            raise Exception, "neither %s nor %s was found" % (convert,anytopnm)
        
        quiet = self._prop['quiet']
        new_files = []
        i = 1 # counter
        for file_ in files:
            new_file = "%s%04d%s" % (basename, i, ofile_ext)
            if app == anytopnm:
                options = ''
                if quiet and app != 'cat':
                    options += '-quiet'
                if app == 'pstopnm':
                    options += ' -stdout'
                    options += ' -portrait'
                cmd = "%(app)s %(options)s %(file_)s " % vars()
                if size is not None and findprograms(pnmscale):
                    w, h = size
                    cmd += "| %(pnmscale)s -width %(w)s -height %(h)s" % vars()
                if pnmtoany != '':
                    options = ''
                    if quiet:
                        options += '-quiet'
                    if pnmtoany == 'pnmtojpeg':
                        options += ' -quality 100' # don't lose quality
                    cmd += " | %(pnmtoany)s %(options)s" % vars()
                cmd += " > %s" % new_file
            else:
                options = ''
                if size is not None:
                    options += '-resize %sx%s' % size
                cmd = "%(app)s %(options)s %(file_)s %(new_file)s" % vars()
            if not quiet: 
                print cmd
            failure = os.system(cmd)
            if failure:
                print "....%s failed, jumping to next file..." % app
                continue
            new_files.append(new_file)
            if not quiet:
                apps = app
                if app != convert and pnmtoany != '':
                    apps += ' and %s' % pnmtoany
                print "%s transformed via %s to %s (%d Kb)" % \
                      (file_,apps,new_file,int(os.path.getsize(new_file)/1000))
            i += 1

        return new_files

    def _get_aspect_ratio(self):
        # accept aspect ratio on the form 4:3, 4/3, or 1.3333
        aspect = self._prop['aspect']
        if isinstance(aspect, str):
            if aspect.find(':') > 0:
                aspect = aspect.split(':')
            elif aspect.find('/'):
                aspect = aspect.split('/')
            else:
                try: aspect = float(aspect)
                except: aspect = None
            try: aspect = float(aspect[0]) / float(aspect[1])
            except: aspect = None
        return aspect

    def _get_size(self):
        legal_sizes = {'sqcif': (128, 96),
                       'qcif': (176, 144),
                       'cif': (352, 288),
                       '4cif': (704, 576)}
        size = self._prop['size']
        if isinstance(size, str):
            if size in legal_sizes:
                size = legal_sizes[size]
            else:
                size = size.split('x') # wxh
        if not (isinstance(size, (tuple,list)) and len(size) == 2):
            size = None
        return size            


def movie(input_files, **kwargs):
    """
    Make a movie from a series of image files. 

    Input arguments:

    input_files -- This argument specifies the image files which will be used
                   to make the movie. The arguemnt must be given as either a
                   string (eg. 'image_*.png') or a list/tuple of strings
                   (eg. glob.glob('image_*.png').

                   Note:
                   
                   - When using the FFmpeg or the Mpeg2enc tools, the image
                     files should be given (if possible) as a string with
                     the format '{1}%{2}d{3}' where the name componentes are
                     as follows:
                     
                       {1} filename prefix (eg. image_)
                       {2} counting placeholder (like in C, printf, eg. 04)
                       {3} file extension (eg. .png or .jpg)

                     A correct description of the files could look like
                     this: 'image_%04d.png'

                   - If the image files is not given on the correct format (as
                     described above), there will be made copies which will
                     then be renamed to the required filename format. This will
                     extend the creation time of the movie.
                     
                   - MEncdoer, FFmpeg, and Mpeg2enc supports only .jpg and .png
                     image files, so if another file format is used, there will
                     be made copies which in turn will be converted to the
                     correct format.
    
    Keyword arguments:

    output_file -- Sets the name of the output movie. If not set, a default
                   name like 'movie.avi' (or 'movie.mpeg' depending on the
                   output format) will be given.

    overwrite_output -- If this is True, the file given in the output_file
                   (above) will be overwritten without warning (if it exists).
                   The default is False.
    
    encoder     -- Sets the encoder tool to be used. Currently the following
                   encoders are supported: 'mencoder', 'ffmpeg', 'mpeg_encode',
                   'ppmtompeg' (from the Netpbm package), and 'mpeg2enc' (from
                   the MJPEGTools package).

                   Note: ppmtompeg and mpeg_encode is the same tool.
      
    vbitrate    -- Sets the bit rate of the movie . The default is 800 kbps.

    vbuffer     -- Sets the video buffer size. The default is to use the 
                   current encoding tools default video buffer size. In some
                   cases it might be necessary to push this up to 500K or more.
       
    fps         -- Sets the number of frames per second for the final movie.
                   The default is 25 fps.

                   Note: the mpeg_encode, ppmtompeg, and mpeg2enc tool only
                   supports the following frame rates: 23.976, 24, 25, 29.97,
                   30, 50, 59.94, and 60 fps.

    vcodec      -- Sets the video codec to be used. Some of the possible codecs
                   are:

                   'mjpeg'      - Motion JPEG
                   'ljpeg'      - Lossless JPEG
                   'h263'       - H.263
                   'h263p'      - H.263+
                   'mpeg4'      - MPEG-4 (DivX 4/5)
                   'msmpeg4'    - DivX 3
                   'msmpeg4v2'  - DivX 3
                   'msmpeg4v2'  - MS MPEG4v2
                   'wmv1'       - Windows Media Video, version 1 (AKA WMV7)
                   'wmv2'       - Windows Media Video, version 2 (AKA WMV8)
                   'rv10'       - an old RealVideo codec
                   'mpeg1video' - MPEG-1 video
                   'mpeg2video' - MPEG-2 video
                   'huffyuv'    - HuffYUV
                   'ffvhuff'    - nonstandard 20% smaller HuffYUV using YV12
                   'asv1'       - ASUS Video v1
                   'asv2'       - ASUS Video v2
                   'ffv1'       - FFmpeg's lossless video codec

                   The default codec is 'mpeg4' for mencoder/ffmpeg and
                   'mpeg1video' for mpeg2enc.

                   Note:
                   
                   - Run 'ffmpeg -formats' for a longer list of available
                     codecs.

                   - The mencoder tool can also use the 'xvid' codec.

                   - Only 'mpeg1video' and 'mpeg2video' is available when
                     using the mpeg2enc tool. 

                   - For the mpeg_encode (and ppmtompeg) encoding tool this
                     option has no effect. 

    qscale      -- The quantization scale value (qscale) give a trade-off
                   between quality and compression. A lower value means better
                   quality but larger files. Lager values gives better
                   compression, but worse quality. The qscale value must be an
                   integer between 1 and 31.
                   The default is to not set the qscale option, that is
                   qscale=None.

                   Note: For the mpeg_encode and ppmtompeg tools, it is
                   possible to have different qscale for I, P, and B frames
                   (see iqscale, pqscale, and bqscale below).

    qmin        -- Minimum quantization scale value. Integer between 1 and 31.
                   Default is 2.

    qmax        -- Maximum quantization scale value. Integer between 1 and 31.
                   Default is 31.

    iqscale     -- Sets the quantization scale (see qscale) for I frames.
                   Only affects mpeg_encode and ppmtompeg. The default is to
                   use the same value as in qscale. If qscale is None, then 8
                   is default value for iqscale.
                   
    pqscale     -- Same as iqscale, but for P frames. If qscale is None, then
                   10 is default value for pqscale.
    
    bqscale     -- Same as iqscale, but for B frames. If qscale is None, then
                   25 is default valie for bqscale.

    pattern     -- Sets the pattern (sequence) of I frames, P frames, and B
                   frames. The default pattern is 'I' which gives good quality
                   (but worse compression). Another standard sequence is
                   'IBBPBBPBBPBBPBB'.

                   Note: this option only effects the mpeg_encode and ppmtompeg
                   encoding tools.
       
    size        -- Sets the size of the movie. The size must be given as
                   either a tuple/list, like (width, height), or as a string.
                   The format of the string must be 'wxh' (eg. '320x240'), but
                   the following abbreviations are also recognized:

                   'sqcif' - 128x96
                   'qcif'  - 176x144
                   'cif'   - 352x288
                   '4cif'  - 704x576

                   The default is to use the size of the input images.

    aspect      -- Sets the aspect ratio of the movie (eg. 4/3 or 16/9).

                   Note:
                   
                   - mpeg_encode and ppmtompeg only supports the following
                     aspect ratios: 1.0, 0.6735, 0.7031, 0.7615,0.8055, 0.8437,
                     0.8935, 0.9157, 0.9815, 1.0255, 1.0695, 1.0950, 1.1575,
                     and 1.2015.

                   - mpeg2enc only supports the following aspect ratios: 1.0,
                     1.33, 1.77, and 2.21.

    prefered_package -- Sets whether to prefer the Netpbm package or the
                  ImageMagick package if both of them are installed. Must be
                  given as a string, that is either 'imagemagick' or 'netpbm'.
                  The default is to use ImageMagick.

                  Note:

                  - If only one of the packages is installed, then that package
                    will be used.

                  - If none of the packages is installed, then some operations
                    might stop in lack of needed programs.

    gop_size    -- Sets the number of frames in a group of pictures (GOP). The
                   default is to use the current encoder tools default value.
       
    quiet       -- If this is True, then the operations will run quietly and
                   only complain on errors. Default is False.

    force_conversion -- Force conversion of images. This is a hack which can
                   be used if the encoding tool has problems reading the input
                   image files. If this is True, the images will be converted
                   even if the they are in a format recognized by the encoding
                   tool. Default is False.

    Examples:
    
    Create a movie (with default values) from a series of png image files named
    img001.png, img002.png, img003.png, ... in the current working directory:

    >>> import easyviz, glob
    >>> images = glob.glob('img*.png')
    >>> easyviz.movie(images)

    or equivalently:

    >>> easyviz.movie('img*.png')

    Create a movie from a series of jpeg files named img01.jpg, img02.jpg, ...
    which lies in the folder /tmp/images using the FFmpeg encoder, with video
    codec 'mpeg2video', video bit rate 2400 kbps, size 320x240, quantization
    scale 4, 25 frames per second, and store the movie in a file called
    movie.avi in the current directory:
    
    >>> easiviz.movie('/tmp/images/img%02d.jpg',
    ...               encoder='ffmpeg',
    ...               vcodec='mpeg2video',
    ...               vbitrate=2400,
    ...               size='320x240',
    ...               qscale=4,
    ...               fps=25)
    ...               output_file='movie.avi')

    """
    me = MovieEncoder(input_files, **kwargs)
    me.encode()


if __name__ == '__main__':
    pass
