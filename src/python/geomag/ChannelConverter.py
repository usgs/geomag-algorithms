#! /usr/bin/env python

import numpy
"""
Convert between different components and coordinate systems used by
the geomagnetic community.

We use three coordinate systems.
Geo: Based on Geographic North.  X, Y, Z
Obs: Based on the observatories orientaion. H, E, Z [d]
Mag: Based on Magnetic North. H, D, Z [E]

d0: Declination baseline in radians
"""

# ###
# get geographic coordinates from....
# ###


def get_geo_from_obs(h, e, d0=0):
    """gets the geographical components given the observatory components.

    Parameters
    __________
    h: float
        the h component from the observatory
    e: float
        the e component from the observatory

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
    h: float
        the total h component in the magnetic north direction.
    d: float
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
    h: float
        the total h component in the magnetic north direction.
    d: float
        the total d declination for the magnetic north direction.

    Returns
    _______
    float
        x component
    """
    return h * numpy.cos(d)


def get_geo_x_from_obs(h, e, d0=0):
    """gets the geographical x component given the observatory components

    Parameters
    __________
    h: float
        the h component from the observatory
    e: float
        the e component from the observatory

    Returns
    _______
    float
        x component
    """
    mag_h = get_mag_h_from_obs(h, e)
    mag_d = get_mag_d_from_obs(h, e, d0)
    return get_geo_x_from_mag(mag_h, mag_d)


def get_geo_y_from_mag(h, d):
    """gets the geographical y component given magnetic north components

    Parameters
    __________
    h: float
        the total h component in the magnetic north direction.
    d: float
        the total d declination for the magnetic north direction.

    Returns
    _______
    float
        y component
    """
    return h * numpy.sin(d)


def get_geo_y_from_obs(h, e, d0=0):
    """gets the geographical y component given the observatory components

    Parameters
    __________
    h: float
        the h component from the observatory
    e: float
        the e component from the observatory

    Returns
    _______
    float
        y component
    """
    mag_h = get_mag_h_from_obs(h, e)
    mag_d = get_mag_d_from_obs(h, e, d0)
    return get_geo_y_from_mag(mag_h, mag_d)


# ###
# get magnetic north coordinates from....
# ###
def get_mag_from_obs(h, e, d0=0):
    """gets the magnetic north components given the observatory components.

    Parameters
    __________
    h: float
        the h component from the observatory
    e: float
        the e component from the observatory

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
    x: float
        the geographic x component
    y: float
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
    h: float
        the h component from the observatory
    e: float
        the e component from the observatory

    Returns
    _______
    float
        the total magnetic declination
    """
    return d0 + get_obs_d_from_obs(h, e)


def get_mag_d_from_geo(x, y):
    """gets the magnetic d component given the geographic components.

    Parameters
    __________
    x: float
        the geographic x component
    y: float
        the geographic y component

    Returns
    _______
    float
        the total magnetic declination
    """
    return numpy.arctan2(y, x)


def get_mag_h_from_obs(h, e):
    """gets the magnetic h component given the observatory components.

    Parameters
    __________
    h: float
        the h component from the observatory
    e: float
        the e component from the observatory

    Returns
    _______
    float
        the total magnetic h component
    """
    return numpy.hypot(h, e)


def get_mag_h_from_geo(x, y):
    """gets the magnetic h component given the geographic components.

    Parameters
    __________
    x: float
        the geographic x component
    y: float
        the geographic y component

    Returns
    _______
    float
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
    x: float
        the geographic x component
    y: float
        the geographic y component

     Returns
    _______
    tuple of array_like
        [0]: observatory h component
        [1]: observatory e component
        [2]: observatory d declination
    """
    mag_h, mag_d = get_mag_from_geo(x, y)
    print mag_h
    print mag_d
    return get_obs_from_mag(mag_h, mag_d, d0)


def get_obs_from_mag(h, d, d0=0):
    """gets the observatory components given the magnetic north components.

    Parameters
    __________
    h: float
        the total h component in the magnetic north direction.
    d: float
        the total d declination for the magnetic north direction.

     Returns
    _______
    tuple of array_like
        [0]: observatory h component
        [1]: observatory e component
        [2]: observatory d declination
    """
    obs_h = get_obs_h_from_mag(h, d, d0)
    obs_e = get_obs_e_from_mag(h, d, d0)
    obs_d = get_obs_d_from_mag(d, d0)
    return (obs_h, obs_e, obs_d)


# inividual get obs from calls
def get_obs_d_from_obs(h, e):
    """gets the observatory d declination given the observatory components.

    Parameters
    __________
    h: float
        the h component from the observatory
    e: float
        the e component from the observatory

    Returns
    _______
    float
        the observatory d declination
    """
    return numpy.arctan2(e, h)


def get_obs_d_from_mag(d, d0=0):
    """gets the observatory d declination given the magnetic north
        declination.

    Parameters
    __________
    d: float
        the total declination d to magnetic north

    Returns
    _______
    float
        the observatory d declination
    """
    return d - d0


def get_obs_e_from_geo(x, y, d0=0):
    """gets the observatory e component given the geographic components.

    Parameters
    __________
    x: float
        the geographic x component
    y: float
        the geographic y component

    Returns
    _______
    float
        the observatory e component
    """
    mag_h = get_mag_h_from_geo(x, y)
    mag_d = get_mag_d_from_geo(x, y)
    return get_obs_e_from_mag(mag_h, mag_d, d0)


def get_obs_e_from_mag(h, d, d0=0):
    """gets the observatory e component given the magnetic components.

    Parameters
    __________
    h: float
        the total h component in the magnetic north direction.
    d: float
        the total d declination for the magnetic north direction.

    Returns
    _______
    float
        the observatory e component
    """
    obs_d = get_obs_d_from_mag(d, d0)
    return h * numpy.sin(obs_d)


def get_obs_e_from_obs(h, d):
    """gets the observatory e component given the observatory components.

    Parameters
    __________
    h: float
        the observatory h component.
    d: float
        the observatory d declination.

    Returns
    _______
    float
        the observatory e component
    """
    return h * numpy.tan(d)


def get_obs_h_from_geo(x, y, d0=0):
    """gets the observatory h component given the geographic components.

    Parameters
    __________
    x: float
        the geographic x component
    y: float
        the geographic y component

    Returns
    _______
    float
        the observatory h component
    """
    mag_h = get_mag_h_from_geo(x, y)
    mag_d = get_mag_d_from_geo(x, y)
    return get_obs_h_from_mag(mag_h, mag_d, d0)


def get_obs_h_from_mag(h, d, d0=0):
    """gets the observatory h component given the magnetic north components

    Parameters
    __________
    h: float
        the total h component in the magnetic north direction.
    d: float
        the total d declination for the magnetic north direction.

    Returns
    _______
    float
        the observatory h component
    """
    obs_d = get_obs_d_from_mag(d, d0)
    return h * numpy.cos(obs_d)

"""
short main to test the principal parts work with geomagnetic data.
"""
if __name__ == '__main__':
    dec_bas = 552.7 * numpy.pi / 60.0 / 180.0
    print "get_geo_x_from_obs", get_geo_x_from_obs(20840.15, -74.16,
            dec_bas)
    print "get_geo_y_from_obs", get_geo_y_from_obs(20840.15, -74.16,
            dec_bas)
    print "get_obs_e_from_geo", get_obs_e_from_geo(20583.260646,
            3262.93317535, dec_bas)
    print "get_obs_h_from_geo", get_obs_h_from_geo(20583.260646,
            3262.93317535, dec_bas)
