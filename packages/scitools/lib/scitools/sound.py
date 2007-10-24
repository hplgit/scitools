import math, numpy, wave, commands, sys, os

max_amplitude = 2**15-1 # iinfo('int16').max if numpy >= 1.0.3

def write(data, filename, channels=1, sample_width=2, sample_rate=44100):
    """
    Writes the array data to the specified file.
    The array data type can be arbitrary as it will be
    converted to numpy.int16 in this function.
    """
    ofile = wave.open(filename, 'w')
    ofile.setnchannels(channels)
    ofile.setsampwidth(sample_width)
    ofile.setframerate(sample_rate)
    ofile.writeframesraw(data.astype(numpy.int16).tostring())
    ofile.close()

def read(filename):
    """
    Read sound data in a file and return the data as an array
    with data type numpy.int16.
    """
    ifile = wave.open(filename)
    channels = ifile.getnchannels()
    sample_width = ifile.getsampwidth()
    sample_rate = ifile.getframerate()
    frames = ifile.getnframes()
    data = ifile.readframes(frames)
    data = numpy.fromstring(data, dtype=numpy.uint16)
    return data.astype(numpy.int16)

def play(soundfile):
    """
    Play a file with name soundfile or an array soundfile.
    (The array is first written to file using the write function
    so the data type can be arbitrary.)
    The player is chosen by the programs open on Mac/Linux and start
    on Windows.
    """
    tmpfile = 'tmp.wav'
    if isinstance(soundfile, numpy.ndarray):
        write(soundfile, tmpfile)
    elif isinstance(soundfile, str):
        tmpfile = soundfile

    if sys.platform[:5] == 'linux':
        status, output = commands.getstatusoutput('open %s' % tmpfile)
        if status != 0:
            # Only for gnome:
            commands.getstatusoutput('gnome-open %s' % tmpfile)
    elif sys.platform == 'darwin':
        commands.getstatusoutput('open %s' %tmpfile)
    else:
        # assume windows
        os.system('start %s' %tmpfile)

def note(frequency, length, amplitude=1, sample_rate=44100):
    """
    Generate the sound of a note as an array if float elements.
    """
    time_points = numpy.linspace(0, length, length*sample_rate)
    data = numpy.sin(2*numpy.pi*frequency*time_points)
    data = amplitude*data
    return data

def add_echo(data, beta=0.8, delay=0.1, sample_rate=44100):
    newdata = data.copy()
    shift = int(delay*sample_rate)  # b (math symbol)
    newdata[shift:] = beta*data[shift:] + \
                      (1-beta)*data[:len(data)-shift]
    #for i in xrange(shift, len(data)):
    #    newdata[i] = beta*data[i] + (1-beta)*data[i-shift]
    return newdata

def _test1():
    filename = 'tmp.wav'

    tone1 = max_amplitude*note(440, 1, 0.2)
    tone2 = max_amplitude*note(293.66, 1, 1)
    tone3 = max_amplitude*note(440, 1, 0.8)
    data = numpy.concatenate((tone1, tone2, tone3))
    write(data, filename)
    data = read(filename)
    play(filename)

def Nothing_Else_Matters(echo=False):
    E1 = note(164.81, .5)
    G = note(392, .5)
    B = note(493.88, .5)
    E2 = note(659.26, .5)
    intro = numpy.concatenate((E1, G, B, E2, B, G))
    high1_long = note(987.77, 1)
    high1_short = note(987.77, .5)
    high2 = note(1046.50, .5)
    high3 = note(880, .5)
    high4_long = note(659.26, 1)
    high4_medium = note(659.26, .5)
    high4_short = note(659.26, .25)
    high5 = note(739.99, .25)
    pause_long =  note(0, .5)
    pause_short = note(0, .25)
    song = numpy.concatenate(
      (intro, intro, high1_long, pause_long, high1_long,
       pause_long, pause_long,
       high1_short, high2, high1_short, high3, high1_short,
       high3, high4_short, pause_short, high4_long, pause_short,
       high4_medium, high5, high4_short))
    song *= max_amplitude
    if echo:
        song = add_echo(song, 0.6)
    return song

if __name__ == '__main__':
    #_test1()
    song = Nothing_Else_Matters(False)
    play(song)
