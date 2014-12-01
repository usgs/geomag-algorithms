#! /usr/bin/env python

import math
"""
Convert between different components and coordinate systems used by
the geomagnetic community.
"""


class ChannelConverter(object):
    """
    Convert between different components and coordinate systems.
    We use three coordinate systems.
    Geo: Based on Geographic North.  X, Y, Z [I]
    Obs: Based on the observatories orientaion. H, E, Z [d]
    Mag: Based on Magnetic North. H, D, Z [E] [G] [F] [compF]
    obs_d0: The Decbas can be set during class initialization.
            Decbas should be in radians.
    Vertical components:
        G: delta F the difference between measured F and computed F.
        F: measured by the proton magnotometer
        compF: computed from the components
        I: inclination
        V: is the geologic vertical component, we use Z instead.
    """

    def __init__(self, obs_d0=0):
        self.obs_d0 = obs_d0

    def set_decbas(self, obs_d0):
        self.obs_d0 = obs_d0

    """
    get geographic coordinates from....
    """
    # general get geo_from_obs save multiple calls.
    def get_geo_from_obs(self, h, e):
        mag_h = self.get_mag_h_from_obs(h, e)
        mag_d = self.get_mag_d_from_obs(h, e)
        geo_x = self.get_geo_x_from_mag(mag_h, mag_d)
        geo_y = self.get_geo_y_from_mag(mag_h, mag_d)
        return (geo_x, geo_y)

    # inividual get geo from calls
    def get_geo_i_from_geo(self, z, f):
        return math.hypot(z, f)

    def get_geo_x_from_obs(self, h, e):
        mag_h = self.get_mag_h_from_obs(h, e)
        mag_d = self.get_mag_d_from_obs(h, e)
        return self.get_geo_x_from_mag(mag_h, mag_d)

    def get_geo_x_from_mag(self, h, d):
        return h * math.cos(d)

    def get_geo_y_from_obs(self, h, e):
        mag_h = self.get_mag_h_from_obs(h, e)
        mag_d = self.get_mag_d_from_obs(h, e)
        return self.get_geo_y_from_mag(mag_h, mag_d)

    def get_geo_y_from_mag(self, h, d):
        return h * math.sin(d)

    def get_geo_z_from_geo(self, i, f):
        return f * math.sin(i)

    """
    get magnetic north coordinates from....
    """
    def get_mag_compf_from_mag(self, h, z):
        return math.hypot(h, z)

    def get_mag_d_from_obs(self, h, e):
        return self.obs_d0 + self.get_obs_d_from_obs(h, e)

    def get_mag_d_from_geo(self, x, y):
        return math.atan2(y, x)

    def get_mag_f_from_mag(self, compf, g):
        return compf - g

    def get_mag_g_from_mag(self, compf, f):
        return f - compf

    def get_mag_h_from_obs(self, h, e):
        return math.hypot(h, e)

    def get_mag_h_from_geo(self, x, y):
        return math.hypot(x, y)

    """
    get observatory coordinates from....
    """
    # general get obs_from_geo save multiple calls.
    def get_obs_from_geo(self, x, y):
        mag_h = self.get_mag_h_from_geo(x, y)
        mag_d = self.get_mag_d_from_geo(x, y)
        obs_e = self.get_obs_e_from_mag(mag_h, mag_d)
        obs_h = self.get_obs_h_from_mag(mag_h, mag_d)
        obs_d = self.get_obs_d_from_mag(mag_d)
        return (obs_h, obs_e, obs_d)

    # inividual get obs from calls
    def get_obs_d_from_obs(self, h, e):
        return math.atan2(e, h)

    def get_obs_d_from_mag(self, d):
        return d - self.obs_d0

    def get_obs_e_from_geo(self, x, y):
        mag_h = self.get_mag_h_from_geo(x, y)
        mag_d = self.get_mag_d_from_geo(x, y)
        return self.get_obs_e_from_mag(mag_h, mag_d)

    def get_obs_e_from_obs(self, h, d):
        return h * math.tan(d)

    def get_obs_e_from_mag(self, h, d):
        obs_d = self.get_obs_d_from_mag(d)
        return h * math.sin(obs_d)

    def get_obs_h_from_geo(self, x, y):
        mag_h = self.get_mag_h_from_geo(x, y)
        mag_d = self.get_mag_d_from_geo(x, y)
        return self.get_obs_h_from_mag(mag_h, mag_d)

    def get_obs_h_from_mag(self, h, d):
        obs_d = self.get_obs_d_from_mag(d)
        return h * math.cos(obs_d)

"""
short main to test the principal parts work with geomagnetic data.
"""
if __name__ == '__main__':
    channel = ChannelConverter((552.7 * math.pi / 60.0 / 180.0))
    print "get_geo_x_from_obs", channel.get_geo_x_from_obs(20840.15, -74.16)
    print "get_geo_y_from_obs", channel.get_geo_y_from_obs(20840.15, -74.16)
    print "get_obs_e_from_geo", channel.get_obs_e_from_geo(20583.260646,
            3262.93317535)
    print "get_obs_h_from_geo", channel.get_obs_h_from_geo(20583.260646,
            3262.93317535)
    print "get_mag_compf_from_mag", channel.get_mag_compf_from_mag(20819.61,
            47705.42)  # Measured f was 52585.28
