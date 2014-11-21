#! /usr/bin/env python

import math
"""
Convert between different components and coordinate systems.
"""


class ChannelConverter(object):
    """
    Convert between different components and coordinate systems.
    We use three coordinate systems.
    Geo: Based on Geologic North.  X, Y, Z
    Obs: Based on the observatories orientaion. H, E, Z [d]
    Mag: Based on Magnetic North. H, D, Z [E]
    obs_d0: The Decbas can be set during class initialization.
            Decbas should be in radians.
    """

    def __init__(self, obs_d0=0):
        self.obs_d0 = obs_d0
        pass

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

    def get_obs_d_from_obs(self, h, e):
        return math.atan2(e, h)

    def get_mag_d_from_obs(self, h, e):
        return self.obs_d0 + self.get_obs_d_from_obs(h, e)

    def get_mag_h_from_obs(self, h, e):
        return math.hypot(h, e)


if __name__ == '__main__':
    channel = ChannelConverter((552.7 * math.pi / 60 / 180))
    print "get_geo_x_from_obs", channel.get_geo_x_from_obs(20840.15, -74.16)
