#! /usr/bin/env python

import math
from nose.tools import assert_equals, assert_sequence_equal
from ChannelConverter import ChannelConverter

sin_45 = math.sin(math.pi / 4)
cos_45 = math.cos(math.pi / 4)
rad_45 = math.pi / 4
tan_45 = math.tan(math.pi / 4)
dec_base_rad = 552.7 * math.pi / 60.0 / 180.0


class ChannelConverterTest:
    @classmethod
    def setup_class(self):
        self.channel = ChannelConverter()    # 5527
        self.channelNoZero = ChannelConverter(dec_base_rad)

    def test_check_decbase(self):
        assert_equals(self.channel.obs_d0, 0)
        assert_equals(self.channelNoZero.obs_d0, dec_base_rad)
        self.channelNoZero.set_decbas(0)
        assert_equals(self.channelNoZero.obs_d0, 0)

    def test_get_geo_from_obs(self):
        assert_sequence_equal(self.channel.get_geo_from_obs(1, math.pi / 4),
                (1, math.pi / 4))

    def test_get_geo_x_from_mag(self):
        assert_equals(self.channel.get_geo_x_from_mag(1, math.pi / 4),
            cos_45)

    def test_get_geo_x_from_obs(self):
        assert_equals(self.channel.get_geo_x_from_obs(1, math.pi / 4),
            1)

    def test_get_geo_y_from_mag(self):
        assert_equals(self.channel.get_geo_x_from_mag(1, math.pi / 4),
            cos_45)

    def test_get_geo_y_from_obs(self):
        assert_equals(self.channel.get_geo_y_from_obs(1, math.pi / 4),
            rad_45)

    def test_get_mag_d_from_obs(self):
        assert_equals(self.channel.get_mag_d_from_obs(2, 2), math.pi / 4)

    def test_get_mag_d_from_geo(self):
        assert_equals(self.channel.get_mag_d_from_obs(2, 2), math.pi / 4)

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
                2 * tan_45)

    def test_get_obs_e_from_mag(self):
        assert_equals(self.channel.get_obs_e_from_mag(1, math.pi / 4),
                sin_45)

    def test_get_obs_h_from_geo(self):
        assert_equals(self.channel.get_obs_h_from_geo(2, math.pi / 4),
                2 * tan_45)

    def test_get_obs_h_from_mag(self):
        assert_equals(self.channel.get_obs_h_from_mag(1, math.pi / 4),
                cos_45)
