import os

from scitools.numpyutils import asarray, ones, seq, shape, reshape, meshgrid, \
     ndarray
import scitools.globaldata

def _update_from_config_file(d, section='easyviz'):
    """
    Update the dictionary d with values from the config file scitools.cfg.
    """
    import pprint
    for key in d:
        data = scitools.globaldata._config_data.get(section,{})
        if key in data:
            try:
                d[key] = data[key][0]
            except Exception as e:
                raise Exception('%s, trying to set key=%s to "%s"' % \
                                (str(e), key, data[key][0]))

def _toggle_state(state):
    if state == 'off' or not state:
        return False
    else:
        return True

def _check_type(var, name, type):
    if not isinstance(var, type):
        raise TypeError('variable "%s"=%s is not of %s' % \
                        (name, var, str(type)))
    else:
        return True

def _check_size(a, a_name, expected_size):
    if isinstance(expected_size, int):
        expected_size = (expected_size,)
    if shape(a) != expected_size:
        raise ValueError('%s has shape %s, expected %s' % \
                         (a_name, a.shape, expected_size))

def _check_xyzv(*args, **kwargs):
    nargs = len(args)
    if nargs == 1:
        x, y, z = [None]*3
        v = asarray(args[0])
    elif nargs == 4:
        x, y, z, v = [asarray(a) for a in args]
    else:
        raise ValueError("_check_xyzv: wrong number of arguments")

    try:
        nx, ny, nz = shape(v)
    except:
        raise ValueError('_check_xyzv: v must be 3D, not %dD' % len(shape(v)))

    indexing = kwargs.get('indexing', 'ij')

    if x is None and y is None and z is None:
        if indexing == 'ij':
            ny, nx = nx, nz  # swap
        x, y, z = meshgrid(list(range(ny)),
                           list(range(nx)),
                           list(range(nz)), indexing=indexing)
    else:
        if indexing == 'ij':
            assert shape(x)==(nx,ny,nz) or shape(x)==(nx,1,1) or \
                   shape(x)==(nx,), \
                   "_check_xyzv: x has shape %s, expected %s, %s, or %s" % \
                   (shape(x), (nx,ny,nz), (nx,1,1), (nx,))

            if shape(x) == (nx,ny,nz):
                assert shape(y) == (nx,ny,nz), \
                       "_check_xyzv: x has shape %s, expected y to be %s, " \
                       "not %s" % (shape(x), (nx,ny,nz), shape(y))
                assert shape(z) == (nx,ny,nz), \
                       "_check_xyzv: x has shape %s, expected z to be %s, " \
                       "not %s" % (shape(x), (nx,ny,nz), shape(z))
            elif shape(x) == (nx,1,1):
                assert shape(y) == (1,ny,1), \
                       "_check_xyzv: x has shape %s, expected y to be %s, " \
                       "not %s" % (shape(x), (1,ny,1), shape(y))
                assert shape(z) == (1,1,nz), \
                       "_check_xyzv: x has shape %s, expected z to be %s, " \
                       "not %s" % (shape(x), (1,1,nz), shape(z))
            else: # shape(x) == (nx,)
                assert shape(y) == (ny,), \
                       "_check_xyzv: x has shape %s, expected y to be %s, " \
                       "not %s" % (shape(x), (ny,), shape(y))
                assert shape(z) == (nz,), \
                       "_check_xyzv: x has shape %s, expected z to be %s, " \
                       "not %s" % (shape(x), (nz,), shape(z))
        else:
            assert shape(x)==(nx,ny,nz) or shape(x)==(1,ny,1) or \
                   shape(x)==(ny,), \
                   "_check_xyzv: x has shape %s, expected %s, %s, or %s" % \
                   (shape(x), (nx,ny,nz), (1,ny,1), (ny,))

            if shape(x) == (nx,ny,nz):
                assert shape(y) == (nx,ny,nz), \
                       "_check_xyzv: x has shape %s, expected y to be %s, " \
                       "not %s" % (shape(x), (nx,ny,nz), shape(y))
                assert shape(z) == (nx,ny,nz), \
                       "_check_xyzv: x has shape %s, expected z to be %s, " \
                       "not %s" % (shape(x), (nx,ny,nz), shape(z))
            elif shape(x) == (1,ny,1):
                assert shape(y) == (nx,1,1), \
                       "_check_xyzv: x has shape %s, expected y to be %s, " \
                       "not %s" % (shape(x), (nx,1,1), shape(y))
                assert shape(z) == (1,1,nz), \
                       "_check_xyzv: x has shape %s, expected z to be %s, " \
                       "not %s" % (shape(x), (1,1,nz), shape(z))
            else: # shape(x) == (ny,)
                assert shape(y) == (nx,), \
                       "_check_xyzv: x has shape %s, expected y to be %s, " \
                       "not %s" % (shape(x), (nx,), shape(y))
                assert shape(z) == (nz,), \
                       "_check_xyzv: x has shape %s, expected z to be %s, " \
                       "not %s" % (shape(x), (nz,), shape(z))

    return x, y, z, v

def _check_xyz(*args, **kwargs):
    nargs = len(args)
    if nargs == 1:
        x, y = [None]*2
        z = asarray(args[0])
    elif nargs == 3:
        x, y, z = [asarray(a) for a in args]
    else:
        raise TypeError("_check_xyz: wrong number of arguments")

    try:
        nx, ny = shape(z)
    except:
        raise ValueError("z must be 2D, not %dD" % len(shape(z)))

    indexing = kwargs.get('indexing', 'ij')

    if x is None and y is None:
        if indexing == 'ij':
            nx, ny = ny, nx  # swap
        x, y = meshgrid(list(range(ny)), list(range(nx)), indexing=indexing)
    else:
        if indexing == 'ij':
            assert shape(x) == (nx,ny) or shape(x) == (nx,1) or len(x) == nx, \
                   "_check_xyz: x has shape %s, expected %s, %s, or %s" % \
                   (shape(x), (nx,ny), (nx,1), (nx,))

            assert shape(y) == (nx,ny) or shape(y) == (1,ny) or len(y) == ny, \
                   "_check_xyz: y has shape %s, expected %s, %s, or %s" % \
                   (shape(y), (nx,ny), (1,ny), (ny,))
        else:
            assert shape(x) == (nx,ny) or shape(x) == (1,ny) or len(x) == ny, \
                   "_check_xyz: x has shape %s, expected %s, %s, or %s" % \
                   (shape(x), (nx,ny), (1,ny), (ny,))

            assert shape(y) == (nx,ny) or shape(y) == (nx,1) or len(y) == nx, \
                   "_check_xyz: y has shape %s, expected %s, %s, or %s" % \
                   (shape(y), (nx,ny), (nx,1), (nx,))

    return x, y, z

def _check_xyuv(*args, **kwargs):
    nargs = len(args)
    if nargs == 2:
        x, y = [None]*2
        u, v = [asarray(a) for a in args]
    elif nargs == 4:
        x, y, u, v = [asarray(a) for a in args]
    else:
        raise TypeError("_check_xyuv: wrong number of arguments")

    indexing = kwargs.get('indexing', 'ij')

    us = shape(u)
    assert us == shape(v), "_check_xyuv: u and v must be of same shape"

    if len(us) == 1:
        if x is None and y is None:
            x = list(range(us[0]))
            y = list(range(us[0]))
        else:
            assert shape(x) == us, \
                   "_check_xyuv: x has shape %s, expected %s" % (shape(x), us)
            assert shape(y) == us, \
                   "_check_xyuv: y has shape %s, expected %s" % (shape(y), us)
    elif len(us) == 2:
        nx, ny = us
        if x is None and y is None:
            if indexing == 'ij':
                x = seq(nx-1)
                y = seq(ny-1)
            else:
                x = seq(ny-1)
                y = seq(nx-1)
        else:
            if indexing == 'ij':
                assert shape(x)==(nx,ny) or shape(x)==(nx,1) or \
                       shape(x)==(nx,), \
                       "_check_xyuv: x has shape %s, expected %s, %s, " \
                       "or %s" % (shape(x), (nx,ny), (nx,1), (nx,))
                assert shape(y)==(nx,ny) or shape(y)==(1,ny) or \
                       shape(y)==(ny,), \
                       "_check_xyuv: y has shape %s, expected %s, %s, " \
                       "or %s" % (shape(y), (nx,ny), (1,ny), (ny,))
            else:
                assert shape(x)==(nx,ny) or shape(x)==(1,ny) or \
                       shape(x)==(ny,), \
                       "_check_xyuv: x has shape %s, expected %s, %s, " \
                       "or %s" % (shape(x), (nx,ny), (1,ny), (ny,))
                assert shape(y)==(nx,ny) or shape(y)==(nx,1) or \
                       shape(y)==(nx,), \
                       "_check_xyuv: y has shape %s, expected %s, %s, " \
                       "or %s" % (shape(y), (nx,ny), (nx,1), (nx,))
    else:
        raise ValueError("_check_xyuv: u must be 1D or 2D, not %dD" % len(us))

    return x, y, u, v

def _check_xyzuvw(*args, **kwargs):
    nargs = len(args)
    if nargs == 4:
        x, y = [None]*2
        z, u, v, w = [asarray(a) for a in args]
    elif nargs == 6:
        x, y, z, u, v, w = [asarray(a) for a in args]
    else:
        raise TypeError("_check_xyzuvw: wrong number of arguments")

    indexing = kwargs.get('indexing', 'xy')

    us = shape(u)
    assert us == shape(v) == shape(w), \
           "_check_xyzuvw: u, v, and w must be of same shape"

    if len(us) == 1:
        if x is None and y is None:
            x = seq(us[0]-1)
            y = seq(us[0]-1)
        else:
            assert shape(x) == us, \
                   "_check_xyuv: x has shape %s, expected %s" % (shape(x), us)
            assert shape(y) == us, \
                   "_check_xyuv: y has shape %s, expected %s" % (shape(y), us)
        assert shape(z) == us, \
               "_check_xyuv: z has shape %s, expected %s" % (shape(z), us)
    elif len(us) == 2:
        nx, ny = us
        if x is None and y is None:
            x, y, z = _check_xyz(z, indexing=indexing)
        else:
            x, y, z = _check_xyz(x, y, z, indexing=indexing)
        assert shape(z) == us, \
               "_check_xyzuvw: z, u, v, and w must be of same shape"
    elif len(us) == 3:
        nx, ny, nz = us
        if x is None and y is None:
            if indexing == 'ij':
                nx, ny = ny, nx  # swap
            x, y, junk = meshgrid(seq(ny-1), seq(nx-1), seq(nz-1))
        else:
            if indexing == 'ij':
                assert shape(x)==us or shape(x)==(nx,1,1) or shape(x)==(nx,), \
                       "_check_xyzuvw: x has shape %s, expected %s, %s, or %s"\
                       % (shape(x), us, (nx,1,1), (nx,))
                assert shape(y)==us or shape(y)==(1,ny,1) or shape(y)==(ny,), \
                       "_check_xyzuvw: y has shape %s, expected %s, %s, or %s"\
                       % (shape(y), us, (1,ny,1), (ny,))
            else:
                assert shape(x)==us or shape(x)==(1,ny,1) or shape(x)==(ny,), \
                       "_check_xyzuvw: x has shape %s, expected %s, %s, or %s"\
                       % (shape(x), us, (1,ny,1), (ny,))
                assert shape(y)==us or shape(y)==(nx,1,1) or shape(y)==(nx,), \
                       "_check_xyzuvw: y has shape %s, expected %s, %s, or %s"\
                       % (shape(y), us, (nx,1,1), (nx,))
        assert shape(z) == us or shape(z) == (1,1,nz) or shape(z) == (nz,), \
               "_check_xyzuvw: z has shape %s, expected %s, %s, or %s" % \
               (shape(z), us, (1,1,nz), (nz,))
    else:
        raise ValueError(
            "_check_xyzuvw: u must be 1D, 2D, or 3D, not %dD" % len(us))

    return x, y, z, u, v, w

def _cmpPlotProperties(a,b):
    """Sort cmp-function for PlotProperties"""
    plotorder = [Volume, Streams, Surface, Contours,
                 VelocityVectors, Bars, Line]
    assert isinstance(a, PlotProperties)
    assert isinstance(b, PlotProperties)
    assert len(PlotProperties.__class__.__subclasses__(PlotProperties)) == \
               len(plotorder) # Check all subclasses is in plotorder
    return cmp(plotorder.index(a.__class__),plotorder.index(b.__class__))
