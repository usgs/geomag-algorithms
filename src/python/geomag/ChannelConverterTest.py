#! /usr/bin/env python

import math
from nose.tools import assert_equals
from ChannelConverter import ChannelConverter


class ChannelConverterTest:
    @classmethod
    def setup_class(self):
        self.channel = ChannelConverter()    # 5527

    def test_check_decbase(self):
        assert_equals(self.channel.obs_d0, 0)

    def test_get_geo_x_from_obs(self):
        # Verify that get_geo_x_from_obs returns correct value.
        assert_equals(self.channel.get_geo_x_from_obs(2, 2),
            2.0000000000000004)

    def test_get_geo_x_from_mag(self):
        # Verify that get_geo_x_from_mag returns correct value.
        assert_equals(self.channel.get_geo_x_from_mag(1, math.pi / 4),
            0.7071067811865476)

    def test_get_geo_y_from_obs(self):
        # Verify that get_geo_y_from_obs returns correct value.
        assert_equals(self.channel.get_geo_y_from_obs(2, 2),
            2.0)

    def test_get_geo_y_from_mag(self):
        # Verify that get_geo_y_from_mag returns correct value.
        assert_equals(self.channel.get_geo_x_from_mag(1, math.pi / 4),
            0.7071067811865476)

    def test_get_mag_h_from_obs(self):
        assert_equals(self.channel.get_mag_h_from_obs(3, 4), 5)

    def test_get_obs_d_from_obs(self):
        assert_equals(self.channel.get_obs_d_from_obs(1, 1),
                45.0 * math.pi / 180.0)
