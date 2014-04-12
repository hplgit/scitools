#!/usr/bin/env python

import os, glob, re

from scitools.misc import findprograms
from misc import _check_type

class MovieEncoder(object):
    """
    Class for turning a series of filenames with frames in a movie into
    a movie file.
    """
    _local_prop = {
        'input_files': None,         # image files
        'output_file': None,         # resulting movie
        'overwrite_output': True,    # overwrite output file if True
        'encoder': None,             # encoding tool
        'vbitrate': None,            # video bit rate
        'vbuffer': None,             # video buffer
        'fps': 25,                   # default frame rate
        'vcodec': 'mpeg4',           # default video codec
        'size': None,                # final movie size
        'quiet': False,              # run in quite mode
        'aspect': None,              # aspect ratio
        'preferred_package': 'ImageMagick',  # prefer ImageMagick or Netpbm
        'qscale': None,              # quantization scale
        'qmin': 2,                   # minimum quantization scale
        'qmax': 31,                  # maximum quantization scale
        'iqscale': None,             # quantization scale for I frames
        'pqscale': None,             # quantization scale for P frames
        'bqscale': None,             # quantization scale for B frames
        'pattern': 'I',              # pattern for I, P, and B frames
        'gop_size': None,            # size of GOP (group of pictures)
        'force_conversion': False,   # force conversion (to png) if True
        'cleanup': True,             # clean up temporary files
        }
    _legal_encoders = 'convert mencoder ffmpeg avconv mpeg_encode ppmtompeg '\
                      'mpeg2enc html'.split()
    _legal_file_types = 'png gif jpg ps eps bmp tif tga pnm'.split()

    def __init__(self, input_files, **kwargs):
        self._prop = {}
        self._prop.update(self._local_prop)
        self._prop['input_files'] = input_files
        for key in kwargs:
            if key in self._prop:
                self._prop[key] = kwargs[key]

        print '\n\n' # provide some space before print statements

        # Determine which encoder to be used
        encoder = self._prop['encoder']
        if encoder is None:
            # No encoder given, find the first installed among the legal ones
            for enc in self._legal_encoders:
                if findprograms(enc):
                    encoder = enc
                    break
            if encoder is None:
                # No encoder is installed, fall back on html
                encoder = 'html'
            self._prop['encoder'] = encoder
        else:
            if not encoder in self._legal_encoders:
                raise ValueError("encoder must be %s, not '%s'" %
                                 (self._legal_encoders, encoder))
            if not encoder.startswith('html') and not findprograms(encoder):
                raise Exception("The selected encoder (%s) is not installed" \
                                % encoder)

        # Determine the file type of the input files
        if isinstance(input_files, (tuple,list)):
            file_ = input_files[0]
        elif isinstance(input_files, str):
            file_ = input_files
        else:
            raise ValueError("The input files must be given as either a "\
                             "list/tuple of strings or a string, not '%s'" % \
                             type(input_files))

        # Check that the input files do exist
        if isinstance(input_files, str):
            # Are input_files on ffmpeg/mpeg2enc format or Unix wildcard format?
            ffmpeg_format = r'(.+)%\d+d(\..+)'
            m = re.search(ffmpeg_format, input_files, re.DOTALL)
            if m:
                wildcard_format = m.group(1) + '*' + m.group(2)
            else:
                wildcard_format = input_files
            all_input_files = glob.glob(wildcard_format)
            if not all_input_files:
                print 'No files of the form %s exist.' % input_files
            else:
                print 'Found %d files of the format %s.' % \
                (len(all_input_files), input_files)
        else:  # list of specific filenames
            all_input_files = input_files
        error_encountered = False
        for f in all_input_files:
            if not os.path.isfile(f):
                print 'Input file %s does not exist.' % f
                error_encountered = True
        if error_encountered:
            raise IOError('Some input files were not found.')

        fname, ext = os.path.splitext(file_)
        if not ext:
            raise ValueError("Unable to determine file type from file name.")
        file_type = ext[1:] # remove the . (dot)
        if not file_type in self._legal_file_types:
            raise TypeError("File type must be %s, not '%s'" % \
                            (self._legal_file_types, file_type))
        self._prop['file_type'] = file_type

    def encode(self):
        """Encode a series of images to a movie."""
        encoder = self._prop['encoder']

        if encoder == 'html':
            # Don't make movie file, just an html file that can play png files
            files = self._prop['input_files']
            if isinstance(files, str):
                files = glob.glob(files)
                files.sort()
            print '\nMaking HTML code for displaying', ', '.join(files)
            fps = self._prop['fps']
            interval_ms = 1000.0/fps
            outf = self._prop['output_file']
            if outf is None:
                outf = 'movie.html'
            else:
                # Ensure .html extension
                outf = os.path.splitext(outf)[0] + '.html'
            casename = os.path.splitext(outf)[0]
            header, jscode, form, footer, files = \
                html_movie(files, interval_ms, casename=casename)

            f = open(outf, 'w')
            f.write(header + jscode + form + footer)
            f.close()
            print "\n\nmovie in output file", outf
            return

        # Get command string (all other encoders are run as stand-alone apps)
        exec('cmd=self._%s()' % encoder)

        # Run command
        if not self._prop['quiet']:
            print "\nscitools.easyviz.movie function runs the command: \n\n%s\n" % cmd
        failure = os.system(cmd)
        if failure:
            print '\n\nscitools.easyviz.movie could not make movie'
            raise SystemError('Check error messages from the encoder in the terminal window')
        elif not self._prop['quiet']:
            print "\n\nmovie in output file", self._prop['output_file']

        # Clean up temporary files
        if self._prop['cleanup'] and hasattr(self, '_tmp_files'):
            for tmp_file in self._tmp_files:
                os.remove(tmp_file)

    def _convert(self):
        """Return a string with commands for making a movie with the convert
        tool (from ImageMagick)."""
        encoder = self._prop['encoder']
        cmd = encoder

        # set number of frames per second:
        #cmd += ' -delay 1x%s' % self._prop['fps']
        cmd += ' -delay %d' % (1.0/self._prop['fps']*100)

        # set size:
        size = self._get_size()
        if size is not None:
            cmd += ' -scale %sx%s' % (size[0], size[1])

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
            files.sort()
        if not files:
            raise ValueError(
                "'%s' is not a valid file specification or the files " \
                "does not exist." % files)
        if isinstance(self._prop['input_files'], str):
            cmd += ' ' + self._prop['input_files']
        else:
            cmd += ' %s' % (' '.join(files))

        # set output file:
        if self._prop['output_file'] is None:
            self._prop['output_file'] = 'movie.gif'
        output_file = self._prop['output_file']
        if output_file[-4:] != '.gif':
            output_file += '.gif'
        if os.path.isfile(output_file) and not self._prop['overwrite_output']:
            raise Exception("Output file '%s' already exist. Use" \
                            " 'overwrite_output=True' to overwrite the file." \
                            % output_file)
        cmd += ' %s' % output_file

        return cmd

    def _mencoder(self):
        """Return a string with commands for making a movie with the MEncoder
        tool.
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
            files.sort()
            if not files:
                raise ValueError(
                    "'%s' is not a valid file specification or the files "\
                    "does not exist." % self._prop['input_files'])
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
        if vbitrate is None:
            vbitrate = 800
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
            raise Exception("Output file '%s' already exist. Use" \
                            " 'overwrite_output=True' to overwrite the file." \
                            % output_file)
        cmd += ' -o %s' % output_file
        if self._prop['quiet']:
            cmd += ' > /dev/null 2>&1'
        return cmd

    def _ffmpeg(self):
        """Return a string with commands for making a movie with the ffmpeg
        tool.
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
                    files.sort()
            else:
                files = glob.glob(files)
                files.sort()
        if isinstance(files, (list,tuple)):
            basename = 'tmp_easyviz_'
            files = self._any2any(files, basename=basename, ofile_ext='.png')
            file_type = 'png'
            self._tmp_files = files[:]
            # create a new string with the right pattern:
            files = basename + '%04d.png'
        cmd += ' -i "%s"' % files
        vbitrate = self._prop['vbitrate']
        if vbitrate is None:
            vbitrate = "800k"
        cmd += ' -b %s' % vbitrate
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

    def _avconv(self):
        """avconv can use same command as ffmpeg."""
        return self._ffmpeg().replace('ffmpeg', 'avconv')

    def _mpeg_encode(self):
        """Return a string with commands for making a movie with the
        mpeg_encode tool.
        """
        encoder = self._prop['encoder']
        basename = 'tmp_easyviz_'  # basename for temporary files

        # set frame rate:
        # mpeg_encode only supports a given set of frame rates:
        legal_frame_rates = (23.976, 24, 25, 29.97, 30, 50, 59.94, 60)
        if self._prop['fps'] in legal_frame_rates:
            fps = self._prop['fps']
        else:
            raise ValueError("%s only supports the these frame rates: %s" % \
                             (encoder, legal_frame_rates))

        # set aspect ratio:
        legal_aspects = (1.0, 0.6735, 0.7031, 0.7615, 0.8055,
                         0.8437, 0.8935, 0.9157, 0.9815, 1.0255,
                         1.0695, 1.0950, 1.1575, 1.2015)
        aspect = self._prop['aspect']
        if aspect is not None:
            if aspect not in legal_aspects:
                raise(ValueError, \
                      "%s only supports the following aspect ratios: %s" % \
                      (encoder, legal_aspects))
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
            files.sort()
        if not files:
            raise ValueError(
                "'%s' is not a valid file specification or the files " \
                "does not exist." % files)
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
            raise Exception("Output file '%s' already exist. Use" \
                            " 'overwrite_output=True' to overwrite the file." \
                            % mpeg_file)

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
        """Return a string with commands for making a movie with the
        mpeg2enc tool (from MJPEGTools).
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
                    files.sort()
            else:
                files = glob.glob(files)
                files.sort()
        if isinstance(files, (list,tuple)):
            basename = 'tmp_easyviz_'
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
            raise Exception("png2yuv or jpeg2yuv is not installed")
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
            raise Exception("Output file '%s' already exist. Use" \
                            " 'overwrite_output=True' to overwrite the file." \
                            % output_file)

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
            raise ValueError("fps must be %s, not %s" % \
                             (fps_convert.keys(), fps))
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
                    raise ValueError(
                        "aspect must be either 1:1, 4:3, 16:9, or 2.21:1," \
                        " not '%s'" % aspect)
            cmd += ' -a %s' % aspect

        # set output file:
        cmd += ' -o %s' % self._prop['output_file']
        if self._prop['quiet']:
            cmd += ' -v 0' # verbosity level 0 (warnings and errors only)
        return cmd

    def _any2any(self, files, basename='tmp_easyviz_',
                 size=None, ofile_ext='.pnm'):
        """Convert a list of files to the file format specified in the
        ofile_ext keyword argument. Using either Netpbm tools or convert
        (from the ImageMagick package).
        """
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
            if self._prop['preferred_package'].lower() == 'imagemagick':
                app = convert
        elif findprograms(convert):
            app = convert
        elif not findprograms((anytopnm, pnmtoany)):
            raise Exception("Neither %s nor %s was found" % (convert,anytopnm))

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
                    #options += ' -portrait'
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
                print "... %s failed, jumping to next file..." % app
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
        """Parse and return the aspect ratio."""
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
        """Parse and return the size."""
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

def html_movie(plotfiles, interval_ms=300, width=800, height=600,
               casename=None):
    """
    Takes a list plotfiles, such as::

        'frame00.png', 'frame01.png', ...

    and creates javascript code for animating the frames as a movie in HTML.

    The `plotfiles` argument can be of three types:

      * A Python list of the names of the image files, sorted in correct
        order. The names can be filenames of files reachable by the
        HTML code, or the names can be URLs.
      * A filename generator using Unix wildcard notation, e.g.,
        ``frame*.png`` (the files most be accessible for the HTML code).
      * A filename generator using printf notation for frame numbering
        and limits for the numbers. An example is ``frame%0d.png:0->92``,
        which means ``frame00.png``, ``frame01.png``, ..., ``frame92.png``.
        This specification of `plotfiles` also allows URLs, e.g.,
        ``http://mysite.net/files/frames/frame_%04d.png:0->320``.

    If `casename` is None, a casename based on the full relative path of the
    first plotfile is used as tag in the variables in the javascript code
    such that the code for several movies can appear in the same file
    (i.e., the various code blocks employ different variables because
    the variable names differ).

    The returned result is text strings that incorporate javascript to
    loop through the plots one after another.  The html text also features
    buttons for controlling the movie.
    The parameter `iterval_ms` is the time interval between loading
    successive images and is in milliseconds.

    The `width` and `height` parameters do not seem to have any effect
    for reasons not understood.

    The following strings are returned: header, javascript code, form
    with movie and buttons, footer, and plotfiles::

       header, jscode, form, footer, plotfiles = html_movie('frames*.png')
       # Insert javascript code in some HTML file
       htmlfile.write(jscode + form)
       # Or write a new standalone file that act as movie player
       filename = plotfiles[0][:-4] + '.html'
       htmlfile = open(filename, 'w')
       htmlfile.write(header + jscode + form + footer)
       htmlfile.close

    This function is based on code written by R. J. LeVeque, based on
    a template from Alan McIntyre.
    """
    # Alternative method:
    # http://stackoverflow.com/questions/9486961/animated-image-with-javascript

    # Start with expanding plotfiles if it is a filename generator
    if not isinstance(plotfiles, (tuple,list)):
        if not isinstance(plotfiles, (str,unicode)):
            raise TypeError('plotfiles must be list or filename generator, not %s' % type(plotfiles))

        filename_generator = plotfiles
        if '*' in filename_generator:
            # frame_*.png
            if filename_generator.startswith('http'):
                raise ValueError('Filename generator %s cannot contain *; must be like http://some.net/files/frame_%%04d.png:0->120' % filename_generator)

            plotfiles = glob.glob(filename_generator)
            if not plotfiles:
                raise ValueError('No plotfiles on the form' %
                                 filename_generator)
            plotfiles.sort()
        elif '->' in filename_generator:
            # frame_%04d.png:0->120
            # http://some.net/files/frame_%04d.png:0->120
            p = filename_generator.split(':')
            filename = ':'.join(p[:-1])
            if not re.search(r'%0?\d+', filename):
                raise ValueError('Filename generator %s has wrong syntax; missing printf specification as in frame_%%04d.png:0->120' % filename_generator)
            if not re.search(r'\d+->\d+', p[-1]):
                raise ValueError('Filename generator %s has wrong syntax; must be like frame_%%04d.png:0->120' % filename_generator)
            p = p[-1].split('->')
            lo, hi = int(p[0]), int(p[1])
            plotfiles = [filename % i for i in range(lo,hi+1,1)]

    # Check that the plot files really exist, if they are local on the computer
    if not plotfiles[0].startswith('http'):
        missing_files = [fname for fname in plotfiles
                         if not os.path.isfile(fname)]
        if missing_files:
            raise ValueError('Missing plot files: %s' %
                             str(missing_files)[1:-1])

    if casename is None:
        # Use plotfiles[0] as the casename, but remove illegal
        # characters in variable names since the casename will be
        # used as part of javascript variable names.
        casename = os.path.splitext(plotfiles[0])[0]
        # Use _ for invalid characters
        casename = re.sub('[^0-9a-zA-Z_]', '_', casename)
        # Remove leading illegal characters until we find a letter or underscore
        casename = re.sub('^[^a-zA-Z_]+', '', casename)

    filestem, ext = os.path.splitext(plotfiles[0])
    if ext == '.png' or ext == '.jpg' or ext == '.jpeg' or ext == 'gif':
        pass
    else:
        raise ValueError('Plotfiles (%s, ...) must be PNG, JPEG, or GIF files with '\
                         'extension .png, .jpg/.jpeg, or .gif' % plotfiles[0])

    header = """\
<html>
<head>
</head>
<body>
"""
    no_images = len(plotfiles)
    jscode = """
<script language="Javascript">
<!---
var num_images_%(casename)s = %(no_images)d;
var img_width_%(casename)s = %(width)d;
var img_height_%(casename)s = %(height)d;
var interval_%(casename)s = %(interval_ms)d;
var images_%(casename)s = new Array();

function preload_images_%(casename)s()
{
   t = document.getElementById("progress");
""" % vars()

    i = 0
    for fname in plotfiles:
        jscode += """
   t.innerHTML = "Preloading image ";
   images_%(casename)s[%(i)s] = new Image(img_width_%(casename)s, img_height_%(casename)s);
   images_%(casename)s[%(i)s].src = "%(fname)s";
        """ % vars()
        i = i+1
    jscode += """
   t.innerHTML = "";
}

function tick_%(casename)s()
{
   if (frame_%(casename)s > num_images_%(casename)s - 1)
       frame_%(casename)s = 0;

   document.name_%(casename)s.src = images_%(casename)s[frame_%(casename)s].src;
   frame_%(casename)s += 1;
   tt = setTimeout("tick_%(casename)s()", interval_%(casename)s);
}

function startup_%(casename)s()
{
   preload_images_%(casename)s();
   frame_%(casename)s = 0;
   setTimeout("tick_%(casename)s()", interval_%(casename)s);
}

function stopit_%(casename)s()
{ clearTimeout(tt); }

function restart_%(casename)s()
{ tt = setTimeout("tick_%(casename)s()", interval_%(casename)s); }

function slower_%(casename)s()
{ interval_%(casename)s = interval_%(casename)s/0.7; }

function faster_%(casename)s()
{ interval_%(casename)s = interval_%(casename)s*0.7; }

// --->
</script>
""" % vars()
    plotfile0 = plotfiles[0]
    form = """
<form>
&nbsp;
<input type="button" value="Start movie" onClick="startup_%(casename)s()">
<input type="button" value="Pause movie" onClick="stopit_%(casename)s()">
<input type="button" value="Restart movie" onClick="restart_%(casename)s()">
&nbsp;
<input type="button" value="Slower" onClick="slower_%(casename)s()">
<input type="button" value="Faster" onClick="faster_%(casename)s()">
</form>

<p><div ID="progress"></div></p>
<img src="%(plotfile0)s" name="name_%(casename)s" border=2/>
""" % vars()
    footer = '\n</body>\n</html>\n'
    return header, jscode, form, footer, plotfiles


def movie(input_files, **kwargs):
    """
    Make a movie from a series of image files.

    This function makes it very easy to create a movie file from a
    series of image files. Several different encoding tools can be
    used, such as an HTML file, MEncoder, ffmpeg, mpeg_encode,
    ppmtompeg (Netpbm), mpeg2enc (MJPEGTools), and convert (ImageMagick),
    to combine the image files together. The encoding tool will be chosen
    automatically among these if more than one is installed on the
    machine in question (unless it is specified as a keyword argument
    to the movie function).

    Suppose we have some image files named `image_0000.eps`, `image_0001.eps`,
    `image_0002.eps`, ... Note that the zero-padding, obtained by the printf
    format `04d` in this case, ensures that the files are listed in correct
    numeric order when using a wildcard notation like `image_*.eps`.
    We want to make a movie out of these files, where each file constitutes
    a frame in the movie. This task can be accomplished by the simple call::

        movie('image_*.eps')

    The result is a movie file with a default name such as `movie.html`,
    `movie.avi`, `movie.mpeg`, or `movie.gif`, depending on the
    encoding tool chosen by the movie function. The file resides in
    the current working directory. The movie function checks a list of
    encoders and chooses the first it finds installed on the computer.

    Note: We strongly recommend to always clean up previously generated
    files for the frames in movies::

        for f in glob.glob('image_*.eps'):
            os.remove(f)

    Otherwise, there is a danger of mixing old and new files in the movie!

    One can easily specify the name of the movie file and explicitly
    specify the encoder. For example, an animated GIF movie can be
    created by::

        movie('image_*.eps', encoder='convert',
              output_file='../wave2D.gif')

    The encoder here is the convert program from the ImageMagick suite
    of image manipulation tools. The resulting movie file will be
    named 'wave2D.gif' and placed in the parent directory.

    Another convenient encoder is simply to make an HTML file that can
    play a series of image files::

        movie('image_*.png', encoder='html',
              output_file='../wave2D.html')

    Just load the output file into a web browser and play the movie.

    If you want to create an MPEG movie by using the MEncoder
    tool, you can do this with the following command::

        movie('image_*.eps', encoder='mencoder',
              output_file='/home/johannr/wave2D.mpeg',
              vcodec='mpeg2video', vbitrate=2400, qscale=4, fps=10)

    Here, we have also specified the video codec to be mpeg2video, the video
    bitrate to be 2400 kbps, the quantization scale (quality) to be 4, and
    the number of frames per second to be 10.

    Demo programs showing various use of the movie function can be
    found as the files movie_demo*.py files in the examples directory
    of the scitools source code tree.

    Suitable movie players are vlc for MPEG and AVI formats, and
    animate for animated GIF files.

    Below follows a more detailed description of the various arguments that
    are available in this function.

    Required arguments:

    input_files: Specifies the image files which will be used to make the
    movie. The argument must be given either as a string,
    e.g., 'image_*.png' or a list/tuple of strings, e.g.,
    glob.glob('image_*.png').

    Notes:

        * When using the ffmpeg or the Mpeg2enc tools, the image
          files should be given (if possible) as a string on the
          format '{1}%{2}d{3}', where the name components are as
          follows:

          - {1} filename prefix (e.g. image_)
          - {2} counting placeholder (like in C, printf, e.g. 04)
          - {3} file extension (e.g. .png or .jpg)

          Example of a correct description of the input files
          is image_%04d.png. If the input files are not given on
          the correct format, there will automatically be made
          copies of these files which will then be renamed to the
          required filename format.

        * MEncoder, ffmpeg, and Mpeg2enc supports only .jpg and
          .png image files. So, if the input files are on another
          format, there will automatically be made copies which
          in turn will be converted to the correct format.

    Optional arguments:

    output_file: Sets the name of the output movie. If not set, a default
    name like movie.avi, movie.mpeg, or movie.gif (depending
    on the output format) will be given.

    Note: When using the convert tool to combine the images,
    the extension of the file name is used to determine the
    file format of the final movie. For example, if a name like
    movie.gif is given, the resulting movie will become an
    animated gif file. Other supported movie formats are MPEG
    (.mpg, .mpeg, or .m2v) and MNG (Multiple-image Network
    Graphics).

    overwrite_output: If True, the file given in the output_file
    argument above will be overwritten without warning (if it already
    exists). The default is True.

    encoder: Sets the encoder tool to be used. Currently the following
    encoders are supported: 'html', 'mencoder', 'ffmpeg',
    'mpeg_encode', 'ppmtompeg' (from the Netpbm package),
    'mpeg2enc' (from the MJPEGTools package), and 'convert'
    (from the ImageMagick package).
    Note: 'ppmtompeg' and 'mpeg_encode' is the same tool.

    vbitrate: Sets the bit rate of the movie. The default is 800 kbps
    when using the ffmpeg and MEncoder encoders. For
    mpeg_encode, ppmtompeg, and mpeg2enc, this option is by
    default not specified. This option has no effect on the
    convert tool from ImageMagick.

    vbuffer: Sets the video buffer size. The default is to use the
    current encoding tools default video buffer size. In some
    cases it might be necessary to push this up to 500K or
    more.

    fps: Sets the number of frames per second for the final movie.
    The default is 25 fps.

    Notes:

     * The 'mpeg_encode', 'ppmtompeg', and 'mpeg2enc' tools only
       supports the following frame rates: 23.976, 24, 25,
       29.97, 30, 50, 59.94, and 60 fps.

     * Not all video codecs have support for arbitrary frame
       rates (e.g., 'mpeg1video' and 'mpeg2video').

    vcodec: Sets the video codec to be used. Some of the possible codecs
    are:

      - 'mjpeg'      - Motion JPEG
      - 'ljpeg'      - Lossless JPEG
      - 'h263'       - H.263
      - 'h263p'      - H.263+
      - 'mpeg4'      - MPEG-4 (DivX 4/5)
      - 'msmpeg4'    - DivX 3
      - 'msmpeg4v2'  - DivX 3
      - 'msmpeg4v2'  - MS MPEG4v2
      - 'wmv1'       - Windows Media Video, version 1 (AKA WMV7)
      - 'wmv2'       - Windows Media Video, version 2 (AKA WMV8)
      - 'rv10'       - an old RealVideo codec
      - 'mpeg1video' - MPEG-1 video
      - 'mpeg2video' - MPEG-2 video
      - 'huffyuv'    - HuffYUV
      - 'ffvhuff'    - nonstandard 20% smaller HuffYUV using YV12
      - 'asv1'       - ASUS Video v1
      - 'asv2'       - ASUS Video v2
      - 'ffv1'       - ffmpeg's lossless video codec

    The default codec is 'mpeg4' for mencoder/ffmpeg and
    'mpeg1video' for mpeg2enc.

    Notes:

      * Run 'ffmpeg -formats' for a longer list of available
        codecs.

      * The mencoder tool can also use the 'xvid' codec.

      * Only 'mpeg1video' and 'mpeg2video' are available when
        using the mpeg2enc tool.

      * This option has no effect when using mpeg_encode,
        ppmtompeg, or convert as the encoding tool.

    qscale: The quantization scale value (qscale) give a trade-off
    between quality and compression. A lower value means better
    quality but larger files. Larger values gives better
    compression, but worse quality. The qscale value must be an
    integer between 1 and 31. The default is to not set the
    qscale option.

    Note: When using mpeg_encode or ppmtompeg it is possible
    to have different qscale values for I, P, and B frames
    (see the iqscale, pqscale, and bqscale options below).

    qmin: Sets the minimum quantization scale value. Must be given as
    an integer between 1 and 31. The default is 2.

    qmax: Sets the maximum quantization scale value. Must be given as
    an integer between 1 and 31. The default is 31.

    iqscale: Sets the quantization scale value (see qscale) for I
    frames. This option only affects mpeg_encode and ppmtompeg.
    The default is to use the same value as in qscale. If
    qscale is not given, then 8 is the default value for
    iqscale.

    pqscale: Same as iqscale, but for P frames. If qscale is not given,
    then 10 is the default value for pqscale.

    bqscale: Same as iqscale, but for B frames. If qscale is not given,
    then 25 is the default value for bqscale.

    pattern: Sets the pattern (sequence) of I, P, and B frames. The
    default pattern is 'I' which gives good quality (but
    worse compression). Another standard sequence is
    'IBBPBBPBBPBBPBB'. This option has only an effect when
    using mpeg_encode or ppmtompeg as the encoding tool.

    size: Sets the size of the final movie. The size must be given
    as a tuple/list (e.g. (640,480)) or as a string. The
    format of the string must be 'wxh' (e.g. '320x240'), but
    the following abbreviations are also recognized:

      - 'sqcif' - 128x96
      - 'qcif'  - 176x144
      - 'cif'   - 352x288
      - '4cif'  - 704x576

    The default is to use the same size as the input images.

    aspect: Sets the aspect ratio of the movie (e.g. 4/3 or 16/9).

    Notes:

      * 'mpeg_encode' and 'ppmtompeg' only support the following
        aspect ratios: 1.0, 0.6735, 0.7031, 0.7615,0.8055,
        0.8437, 0.8935, 0.9157, 0.9815, 1.0255, 1.0695, 1.0950,
        1.1575, and 1.2015.

      * 'mpeg2enc' only supports the following aspect ratios: 1.0,
        1.33, 1.77, and 2.21.

    preferred_package: Sets whether to prefer the Netpbm package or the
    ImageMagick package if both of them are installed. Must be
    given as a string, i.e, either 'imagemagick' (default) or
    'netpbm'.

    Notes:

      * If only one of the packages is installed, then that
        package will be used.

      * If none of the packages are installed, then some
        operations might stop in lack of needed programs.

    gop_size: Sets the number of frames in a group of pictures (GOP).
    The default is to use the chosen encoding tools default
    value.

    quiet: If True, then the operations will run quietly and only
    complain on errors. The default is False.

    cleanup: If True (default), all temporary files that are created
    during the execution of the movie command will be deleted.

    force_conversion: Forces conversion of images. This is a hack that can
    be used if the encoding tool has problems reading the input
    image files. If this is set to True, the images will be
    converted even if they are in a format recognized by the
    encoding tool. The default is False.

    Known issues:

      * JPEG images created by the Vtk backend does not seem to work with
        the MEncoder and ffmpeg tools. This can be fixed by setting the
        force_conversion argument to True. This will force conversion of the
        JPEG files to PNG files which in turn should successfully create the
        movie.

      * Aspect ratio in mpeg_encode does not seem to work.
    """
    me = MovieEncoder(input_files, **kwargs)
    me.encode()


if __name__ == '__main__':
    pass
