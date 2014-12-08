#! /usr/bin/env python

import numpy
from nose.tools import assert_equals, assert_sequence_equal
from nose.tools import assert_almost_equal
import ChannelConverter as channel

sin_45 = numpy.sin(numpy.pi / 4)
cos_45 = numpy.cos(numpy.pi / 4)
rad_45 = numpy.pi / 4
tan_45 = numpy.tan(numpy.pi / 4)
dec_base_rad = 552.7 * numpy.pi / 60.0 / 180.0


class ChannelConverterTest:
    """Unit Tests for ChannelConverter
    """

    def test_get_geo_from_obs(self):
        assert_sequence_equal(channel.get_geo_from_obs(1, rad_45),
                (1, rad_45))

    def test_get_geo_x_from_mag(self):
        assert_equals(channel.get_geo_x_from_mag(1, rad_45),
            cos_45)

    def test_get_geo_x_from_obs(self):
        assert_equals(channel.get_geo_x_from_obs(1, rad_45),
            1)

    def test_get_geo_y_from_mag(self):
        assert_equals(channel.get_geo_x_from_mag(1, rad_45),
            cos_45)

    def test_get_geo_y_from_obs(self):
        assert_equals(channel.get_geo_y_from_obs(1, rad_45),
            rad_45)

    def test_get_mag_d_from_obs(self):
        assert_equals(channel.get_mag_d_from_obs(2, 2), rad_45)

    def test_get_mag_d_from_geo(self):
        assert_equals(channel.get_mag_d_from_obs(2, 2), rad_45)

    def test_get_mag_h_from_obs(self):
        assert_equals(channel.get_mag_h_from_obs(3, 4), 5)

    def test_get_mag_h_from_geo(self):
        assert_equals(channel.get_mag_h_from_geo(3, 4), 5)

    def test_get_obs_from_geo(self):
        """geomag.io.channelTest.test_get_obs_from_geo()

        This test produces a computing error. The tuple should be,
        (1.0, 1.0, rad_45).
        Second test comes out correct, testing the case where observatory
        is aligned with geographic north.
        """
        assert_sequence_equal(channel.get_obs_from_geo(1, 0),
                (1.0, 0, 0.0))
        obs = channel.get_obs_from_geo(1, 1)
        assert_almost_equal(obs[0], 1.0, places=8)
        assert_almost_equal(obs[0], 1.0, places=8)
        assert_almost_equal(obs[0], tan_45, places=8)

    def test_get_obs_d_from_obs(self):
        assert_equals(channel.get_obs_d_from_obs(1, 1),
                numpy.pi / 4)

    def test_get_obs_d_from_mag(self):
        assert_equals(channel.get_obs_d_from_mag(1), 1)

    def test_get_obs_e_from_geo(self):
        assert_equals(channel.get_obs_e_from_geo(2, 2), 2)

    def test_get_obs_e_from_obs(self):
        assert_equals(channel.get_obs_e_from_obs(2, rad_45),
                2 * tan_45)

    def test_get_obs_e_from_mag(self):
        assert_equals(channel.get_obs_e_from_mag(1, rad_45),
                sin_45)

    def test_get_obs_h_from_geo(self):
        assert_equals(channel.get_obs_h_from_geo(2, rad_45),
                2 * tan_45)

    def test_get_obs_h_from_mag(self):
        assert_equals(channel.get_obs_h_from_mag(1, rad_45),
                cos_45)
