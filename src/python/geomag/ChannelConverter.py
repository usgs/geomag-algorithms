#! /usr/bin/env python

import numpy
"""
Convert between different components and coordinate systems used by
the geomagnetic community.
"""


class ChannelConverter(object):
    """Convert between different components and coordinate systems.

    Attributes
    __________
    obs_d0: float
        The Decbas for the observatory. Short for Declination Baseline.
        We expect Decbas to be in radians.

    Notes
    _____
    We use three coordinate systems.
    Geo: Based on Geographic North.  X, Y, Z
    Obs: Based on the observatories orientaion. H, E, Z [d]
    Mag: Based on Magnetic North. H, D, Z [E]
    """

    def __init__(self, obs_d0=0):
        self.obs_d0 = obs_d0

    def set_decbas(self, obs_d0):
        """set the declination base

        Parameters
        __________
        obs_d0: float
        """
        self.obs_d0 = obs_d0

    # ###
    # get geographic coordinates from....
    # ###
    def get_geo_from_obs(self, h, e):
        """gets the geographical components given the observatory components.

        Parameters
        __________
        h: float
            the h component from the observatory
        e: float
            the e component from the observatory

        Returns
        _______
        tuple
            [0]: x component as a float
            [1]: y component as a float
        """
        mag = self.get_mag_from_obs(h, e)
        return self.get_geo_from_mag(mag[0], mag[1])

    def get_geo_from_mag(self, h, d):
        """gets the geographical components given the magnetic components

        Parameters
        __________
        h: float
            the total h component in the magnetic north direction.
        d: float
            the total d declination for the magnetic north direction.

        Returns
        _______
        tuple
            geo_x: x component as a float
            geo_y: y component as a float
        """
        geo_x = self.get_geo_x_from_mag(h, d)
        geo_y = self.get_geo_y_from_mag(h, d)
        return (geo_x, geo_y)

    # inividual get geo from calls
    def get_geo_x_from_obs(self, h, e):
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
        mag_h = self.get_mag_h_from_obs(h, e)
        mag_d = self.get_mag_d_from_obs(h, e)
        return self.get_geo_x_from_mag(mag_h, mag_d)

    def get_geo_x_from_mag(self, h, d):
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

    def get_geo_y_from_obs(self, h, e):
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
        mag_h = self.get_mag_h_from_obs(h, e)
        mag_d = self.get_mag_d_from_obs(h, e)
        return self.get_geo_y_from_mag(mag_h, mag_d)

    def get_geo_y_from_mag(self, h, d):
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

    # ###
    # get magnetic north coordinates from....
    # ###
    def get_mag_from_obs(self, h, e):
        """gets the magnetic north components given the observatory components.

        Parameters
        __________
        h: float
            the h component from the observatory
        e: float
            the e component from the observatory

        Returns
        _______
        tuple
            [0]: total h component as a float
            [1]: total d declination as a float
        """
        mag_h = self.get_mag_h_from_obs(h, e)
        mag_d = self.get_mag_d_from_obs(h, e)
        return (mag_h, mag_d)

    def get_mag_from_geo(self, x, y):
        """gets the magnetic north components given the geographic components.

        Parameters
        __________
        x: float
            the geographic x component
        y: float
            the geographic y component

        Returns
        _______
        tuple
            [0]: total h component as a float
            [1]: total d declination as a float
        """
        mag_h = self.get_mag_h_from_geo(x, y)
        mag_d = self.get_mag_d_from_geo(x, y)
        return (mag_h, mag_d)

    def get_mag_d_from_obs(self, h, e):
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
        return self.obs_d0 + self.get_obs_d_from_obs(h, e)

    def get_mag_d_from_geo(self, x, y):
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

    def get_mag_h_from_obs(self, h, e):
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

    def get_mag_h_from_geo(self, x, y):
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
    def get_obs_from_geo(self, x, y):
        """gets the observatory components given the geographic components.

        Parameters
        __________
        x: float
            the geographic x component
        y: float
            the geographic y component

         Returns
        _______
        tuple
            [0]: observatory h component
            [1]: observatory e component
            [1]: observatory d declination
        """
        mag = self.get_mag_from_geo(x, y)
        return self.get_obs_from_mag(mag[0], mag[1])

    def get_obs_from_mag(self, h, d):
        """gets the observatory components given the magnetic north components.

        Parameters
        __________
        h: float
            the total h component in the magnetic north direction.
        d: float
            the total d declination for the magnetic north direction.

         Returns
        _______
        tuple
            [0]: observatory h component
            [1]: observatory e component
            [1]: observatory d declination
        """
        obs_h = self.get_obs_h_from_mag(h, d)
        obs_e = self.get_obs_e_from_mag(h, d)
        obs_d = self.get_obs_d_from_mag(d)
        return (obs_h, obs_e, obs_d)

    # inividual get obs from calls
    def get_obs_d_from_obs(self, h, e):
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

    def get_obs_d_from_mag(self, d):
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
        return d - self.obs_d0

    def get_obs_e_from_geo(self, x, y):
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
        mag_h = self.get_mag_h_from_geo(x, y)
        mag_d = self.get_mag_d_from_geo(x, y)
        return self.get_obs_e_from_mag(mag_h, mag_d)

    def get_obs_e_from_mag(self, h, d):
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
        obs_d = self.get_obs_d_from_mag(d)
        return h * numpy.sin(obs_d)

    def get_obs_e_from_obs(self, h, d):
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

    def get_obs_h_from_geo(self, x, y):
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
        mag_h = self.get_mag_h_from_geo(x, y)
        mag_d = self.get_mag_d_from_geo(x, y)
        return self.get_obs_h_from_mag(mag_h, mag_d)

    def get_obs_h_from_mag(self, h, d):
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
        obs_d = self.get_obs_d_from_mag(d)
        return h * numpy.cos(obs_d)

"""
short main to test the principal parts work with geomagnetic data.
"""
if __name__ == '__main__':
    channel = ChannelConverter((552.7 * numpy.pi / 60.0 / 180.0))
    print "get_geo_x_from_obs", channel.get_geo_x_from_obs(20840.15, -74.16)
    print "get_geo_y_from_obs", channel.get_geo_y_from_obs(20840.15, -74.16)
    print "get_obs_e_from_geo", channel.get_obs_e_from_geo(20583.260646,
            3262.93317535)
    print "get_obs_h_from_geo", channel.get_obs_h_from_geo(20583.260646,
            3262.93317535)
