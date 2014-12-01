#! /usr/bin/env python

import math
from nose.tools import assert_equals, assert_sequence_equal
from ChannelConverter import ChannelConverter


class ChannelConverterTest:
    @classmethod
    def setup_class(self):
        self.channel = ChannelConverter()    # 5527

    def test_check_decbase(self):
        assert_equals(self.channel.obs_d0, 0)

    def test_get_geo_from_obs(self):
        assert_sequence_equal(self.channel.get_geo_from_obs(1, math.pi / 4),
                (1, math.pi / 4))

    def test_get_geo_i_from_geo(self):
        assert_equals(self.channel.get_geo_i_from_geo(2, 2), math.sqrt(8))

    def test_get_geo_x_from_mag(self):
        # Verify that get_geo_x_from_mag returns correct value.
        assert_equals(self.channel.get_geo_x_from_mag(1, math.pi / 4),
            0.7071067811865476)

    def test_get_geo_x_from_obs(self):
        # Verify that get_geo_x_from_obs returns correct value.
        assert_equals(self.channel.get_geo_x_from_obs(1, math.pi / 4),
            1)

    def test_get_geo_y_from_mag(self):
        # Verify that get_geo_y_from_mag returns correct value.
        assert_equals(self.channel.get_geo_x_from_mag(1, math.pi / 4),
            0.7071067811865476)

    def test_get_geo_y_from_obs(self):
        # Verify that get_geo_y_from_obs returns correct value.
        assert_equals(self.channel.get_geo_y_from_obs(1, math.pi / 4),
            math.pi / 4)

    def test_get_geo_z_from_geo(self):
        assert_equals(self.channel.get_geo_z_from_geo(math.pi / 4, 1),
            0.7071067811865475)

    def test_get_mag_d_from_obs(self):
        assert_equals(self.channel.get_mag_d_from_obs(2, 2), math.pi / 4)

    def test_get_mag_d_from_geo(self):
        assert_equals(self.channel.get_mag_d_from_obs(2, 2), math.pi / 4)

    def test_get_mag_compf_from_mag(self):
        assert_equals(self.channel.get_mag_compf_from_mag(2, 2), math.sqrt(8))

    def test_get_mag_f_from_mag(self):
        assert_equals(self.channel.get_mag_f_from_mag(2, 1), 1)

    def test_get_mag_g_from_mag(self):
        assert_equals(self.channel.get_mag_g_from_mag(1, 2), 1)

    def test_get_mag_h_from_obs(self):
        assert_equals(self.channel.get_mag_h_from_obs(3, 4), 5)

    def test_get_mag_h_from_geo(self):
        assert_equals(self.channel.get_mag_h_from_geo(3, 4), 5)

    def test_get_obs_from_geo(self):
        assert_sequence_equal(self.channel.get_obs_from_geo(1, math.pi / 4),
                (1.0, math.pi / 4, 0.6657737500283538))

    def test_get_obs_d_from_obs(self):
        assert_equals(self.channel.get_obs_d_from_obs(1, 1),
                math.pi / 4)

    def test_get_obs_d_from_mag(self):
        assert_equals(self.channel.get_obs_d_from_mag(1), 1)

    def test_get_obs_e_from_geo(self):
        assert_equals(self.channel.get_obs_e_from_geo(2, 2), 2)

    def test_get_obs_e_from_obs(self):
        assert_equals(self.channel.get_obs_e_from_obs(2, math.pi / 4),
                1.9999999999999998)

    def test_get_obs_e_from_mag(self):
        assert_equals(self.channel.get_obs_e_from_mag(1, math.pi / 4),
                0.7071067811865475)

    def test_get_obs_h_from_geo(self):
        assert_equals(self.channel.get_obs_h_from_geo(2, math.pi / 4),
                1.9999999999999998)

    def test_get_obs_h_from_mag(self):
        assert_equals(self.channel.get_obs_h_from_mag(1, math.pi / 4),
                0.7071067811865476)
