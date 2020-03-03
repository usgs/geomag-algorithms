"""
Convert between different components and coordinate systems used by
the geomagnetic community.

We use three coordinate systems.
Geo: Based on Geographic North.  X, Y, Z
     X is north, Y is east
Obs: Based on the observatories orientaion. H, E, Z [d]
Mag: Based on Magnetic North. H, D, Z [E]

d0: Declination baseline in radians

Notes: We use numpy functions instead of standard python arithmetic funtions
    for 2 reasons.  1) so that either array's can be passed in, or individual
    values. 2) Because they are more flexible/robust then the standard python
    functions.
"""


import numpy


M2R = numpy.pi / 180 / 60  # Minutes to Radians
R2M = 180.0 / numpy.pi * 60  # Radians to Minutes


# ###
# get geographic coordinates from....
# ###


def get_geo_from_obs(h, e, d0=0):
    """gets the geographical components given the observatory components.

    Parameters
    __________
    h: array_like
        the h component from the observatory
    e: array_like
        the e component from the observatory
    d0: float
        the declination baseline angle in radians

    Returns
    _______
    tuple of array_like
        [0]: x component as a float
        [1]: y component as a float
    """
    mag_h, mag_d = get_mag_from_obs(h, e, d0)
    return get_geo_from_mag(mag_h, mag_d)


def get_geo_from_mag(h, d):
    """gets the geographical components given the magnetic components

    Parameters
    __________
    h: array_like
        the total h component in the magnetic north direction.
    d: array_like
        the total d declination for the magnetic north direction.

    Returns
    _______
    tuple of array_like
        geo_x: x component as a float
        geo_y: y component as a float
    """
    geo_x = get_geo_x_from_mag(h, d)
    geo_y = get_geo_y_from_mag(h, d)
    return (geo_x, geo_y)


# inividual get geo from calls
def get_geo_x_from_mag(h, d):
    """gets the geographical x component given magnetic north components

    Parameters
    __________
    h: array_like
        the total h component in the magnetic north direction.
    d: array_like
        the total d declination for the magnetic north direction.

    Returns
    _______
    array_like
        x component
    """
    return numpy.multiply(h, numpy.cos(d))


def get_geo_y_from_mag(h, d):
    """gets the geographical y component given magnetic north components

    Parameters
    __________
    h: array_like
        the total h component in the magnetic north direction.
    d: array_like
        the total d declination for the magnetic north direction.

    Returns
    _______
    array_like
        y component
    """
    return numpy.multiply(h, numpy.sin(d))


# ###
# get magnetic north coordinates from....
# ###
def get_mag_from_obs(h, e, d0=0):
    """gets the magnetic north components given the observatory components.

    Parameters
    __________
    h: array_like
        the h component from the observatory
    e: array_like
        the e component from the observatory
    d0: float
        the declination baseline angle in radians

    Returns
    _______
    tuple of array_like
        [0]: total h component as a float
        [1]: total d declination as a float
    """
    mag_h = get_mag_h_from_obs(h, e)
    mag_d = get_mag_d_from_obs(h, e, d0)
    return (mag_h, mag_d)


def get_mag_from_geo(x, y):
    """gets the magnetic north components given the geographic components.

    Parameters
    __________
    x: array_like
        the geographic x component
    y: array_like
        the geographic y component

    Returns
    _______
    tuple of array_like
        [0]: total h component as a float
        [1]: total d declination as a float
    """
    mag_h = get_mag_h_from_geo(x, y)
    mag_d = get_mag_d_from_geo(x, y)
    return (mag_h, mag_d)


def get_mag_d_from_obs(h, e, d0=0):
    """gets the magnetic d component given the observatory components.

    Parameters
    __________
    h: array_like
        the h component from the observatory
    e: array_like
        the e component from the observatory
    d0: float
        the declination baseline angle in radians

    Returns
    _______
    array_like
        the total magnetic declination
    """
    return numpy.add(d0, get_obs_d_from_obs(h, e))


def get_mag_d_from_geo(x, y):
    """gets the magnetic d component given the geographic components.

    Parameters
    __________
    x: array_like
        the geographic x component
    y: array_like
        the geographic y component

    Returns
    _______
    array_like
        the total magnetic declination
    """
    return numpy.arctan2(y, x)


def get_mag_h_from_obs(h, e):
    """gets the magnetic h component given the observatory components.

    Parameters
    __________
    h: array_like
        the h component from the observatory
    e: array_like
        the e component from the observatory

    Returns
    _______
    array_like
        the total magnetic h component
    """
    return numpy.hypot(h, e)


def get_mag_h_from_geo(x, y):
    """gets the magnetic h component given the geographic components.

    Parameters
    __________
    x: array_like
        the geographic x component
    y: array_like
        the geographic y component

    Returns
    _______
    array_like
        the total magnetic h component
    """
    return numpy.hypot(x, y)


# ###
# get observatory coordinates from....
# ###
def get_obs_from_geo(x, y, d0=0):
    """gets the observatory components given the geographic components.

    Parameters
    __________
    x: array_like
        the geographic x component
    y: array_like
        the geographic y component
    d0: float
        the declination baseline angle in radians

     Returns
    _______
    tuple of array_like
        [0]: observatory h component
        [1]: observatory e component
        [2]: observatory d declination
    """
    mag_h, mag_d = get_mag_from_geo(x, y)
    return get_obs_from_mag(mag_h, mag_d, d0)


def get_obs_from_mag(h, d, d0=0):
    """gets the observatory components given the magnetic north components.

    Parameters
    __________
    h: array_like
        the total h component in the magnetic north direction.
    d: array_like
        the total d declination for the magnetic north direction.
    d0: float
        the declination baseline angle in radians

     Returns
    _______
    tuple of array_like
        [0]: observatory h component
        [1]: observatory e component
        [2]: observatory d declination
    """
    obs_h = get_obs_h_from_mag(h, d, d0)
    obs_e = get_obs_e_from_mag(h, d, d0)
    return (obs_h, obs_e)


# inividual get obs from calls
def get_obs_d_from_obs(h, e):
    """gets the observatory d declination given the observatory components.

    Parameters
    __________
    h: array_like
        the h component from the observatory
    e: array_like
        the e component from the observatory

    Returns
    _______
    array_like
        the observatory d declination
    """
    return numpy.arctan2(e, h)


def get_obs_d_from_mag_d(d, d0=0):
    """gets the observatory d declination given the magnetic north
        declination.

    Parameters
    __________
    d: array_like
        the total declination d to magnetic north
    d0: float
        the declination baseline angle in radians

    Returns
    _______
    array_like
        the observatory d declination
    """
    return numpy.subtract(d, d0)


def get_obs_e_from_mag(h, d, d0=0):
    """gets the observatory e component given the magnetic components.

    Parameters
    __________
    h: array_like
        the total h component in the magnetic north direction.
    d: array_like
        the total d declination for the magnetic north direction.
    d0: float
        the declination baseline angle in radians

    Returns
    _______
    array_like
        the observatory e component
    """
    obs_d = get_obs_d_from_mag_d(d, d0)
    return numpy.multiply(h, numpy.sin(obs_d))


def get_obs_e_from_obs(h, d):
    """gets the observatory e component given the observatory components.

    Parameters
    __________
    h: array_like
        the observatory h component.
    d: array_like
        the observatory d declination.

    Returns
    _______
    array_like
        the observatory e component
    """
    return numpy.multiply(h, numpy.tan(d))


def get_obs_h_from_mag(h, d, d0=0):
    """gets the observatory h component given the magnetic north components

    Parameters
    __________
    h: array_like
        the total h component in the magnetic north direction.
    d: array_like
        the total d declination for the magnetic north direction.
    d0: float
        the declination baseline angle in radians

    Returns
    _______
    array_like
        the observatory h component
    """
    obs_d = get_obs_d_from_mag_d(d, d0)
    return numpy.multiply(h, numpy.cos(obs_d))


def get_deltaf(fv, fs):
    """gets the deltaf value given the scalar F and computed F values.

    Parameters
    ----------
    fv: array_like
        the F vector computed from the observatory instruments
    fs: array_like
        the measured F value
    """
    return numpy.subtract(fv, fs)


def get_computed_f_using_squares(x, y, z):
    """gets the computed f value

    Parameters
    ----------
    x: array_like
        the x component from the observatory
    y: array_like
        the y component from the observatory
    z: array_like
        the z component from the observatory
    Notes
    -----
    This works for geographic coordinates, or observatory coordinates.
        ie x, y, z or h, e, z
        We're using variables x,y,z to represent generic cartisian coordinates.
    """
    x2 = numpy.square(x)
    y2 = numpy.square(y)
    z2 = numpy.square(z)
    fv = numpy.add(x2, y2)
    fv = numpy.add(fv, z2)
    return numpy.sqrt(fv)


def get_radians_from_minutes(m):
    """gets the radian value given the decimal value
    Parameters
    __________
    d: array_like
        the decimal value to be converted
    """
    return numpy.multiply(m, M2R)


def get_minutes_from_radians(r):
    """gets the decimal value given the radian value

    Parameters
    __________
    r: float
        the radian value to be converted
    """
    return numpy.multiply(r, R2M)
