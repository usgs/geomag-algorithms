#! /usr/bin/env python

import numpy
from nose.tools import assert_equals, assert_sequence_equal
from ChannelConverter import ChannelConverter

sin_45 = numpy.sin(numpy.pi / 4)
cos_45 = numpy.cos(numpy.pi / 4)
rad_45 = numpy.pi / 4
tan_45 = numpy.tan(numpy.pi / 4)
dec_base_rad = 552.7 * numpy.pi / 60.0 / 180.0


class ChannelConverterTest:
    """Unit Tests for ChannelConverter

        Unit test for ChannelConverter, taking advantage of the
        setup_class methods of nose to instantiate a single
        ChannelConverter test to be used by all tests.

    Attributes
    __________
    obs_d0: float
        The Decbas for the observatory. Short for Declination Baseline.
        We expect Decbas to be in radians.

    Notes
    _____
    Most of these tests are unnecessary, but for consistency sake, we test all
    of the base functions using simple 45 degrees to test the trig functions.
    """

    @classmethod
    def setup_class(self):
        self.channel = ChannelConverter()    # 5527
        self.channelNoZero = ChannelConverter(dec_base_rad)

    def test_check_decbas(self):
        """geomag.io.ChannelConverterTest.test_check_decbas()

        Confirm that a newly instantiated ChannelConverter,
            defaults to decbas 0,
            and uses an instantiated value.
        Confirm that set_decbas works.
        """
        assert_equals(self.channel.obs_d0, 0)
        assert_equals(self.channelNoZero.obs_d0, dec_base_rad)
        self.channelNoZero.set_decbas(0)
        assert_equals(self.channelNoZero.obs_d0, 0)

    def test_get_geo_from_obs(self):
        assert_sequence_equal(self.channel.get_geo_from_obs(1, rad_45),
                (1, rad_45))

    def test_get_geo_x_from_mag(self):
        assert_equals(self.channel.get_geo_x_from_mag(1, rad_45),
            cos_45)

    def test_get_geo_x_from_obs(self):
        assert_equals(self.channel.get_geo_x_from_obs(1, rad_45),
            1)

    def test_get_geo_y_from_mag(self):
        assert_equals(self.channel.get_geo_x_from_mag(1, rad_45),
            cos_45)

    def test_get_geo_y_from_obs(self):
        assert_equals(self.channel.get_geo_y_from_obs(1, rad_45),
            rad_45)

    def test_get_mag_d_from_obs(self):
        assert_equals(self.channel.get_mag_d_from_obs(2, 2), rad_45)

    def test_get_mag_d_from_geo(self):
        assert_equals(self.channel.get_mag_d_from_obs(2, 2), rad_45)

    def test_get_mag_h_from_obs(self):
        assert_equals(self.channel.get_mag_h_from_obs(3, 4), 5)

    def test_get_mag_h_from_geo(self):
        assert_equals(self.channel.get_mag_h_from_geo(3, 4), 5)

    def test_get_obs_from_geo(self):
        """geomag.io.ChannelConverterTest.test_get_obs_from_geo()

        This test produces a computing error. The tuple should be,
        (1.0, 1.0, rad_45).
        Second test comes out correct, testing the case where observatory
        is aligned with geographic north.
        """
        assert_sequence_equal(self.channel.get_obs_from_geo(1, 1),
                (1.0000000000000002, 1.0, 0.78539816339744828))
        assert_sequence_equal(self.channel.get_obs_from_geo(1, 0),
                (1.0, 0, 0.0))

    def test_get_obs_d_from_obs(self):
        assert_equals(self.channel.get_obs_d_from_obs(1, 1),
                numpy.pi / 4)

    def test_get_obs_d_from_mag(self):
        assert_equals(self.channel.get_obs_d_from_mag(1), 1)

    def test_get_obs_e_from_geo(self):
        assert_equals(self.channel.get_obs_e_from_geo(2, 2), 2)

    def test_get_obs_e_from_obs(self):
        assert_equals(self.channel.get_obs_e_from_obs(2, rad_45),
                2 * tan_45)

    def test_get_obs_e_from_mag(self):
        assert_equals(self.channel.get_obs_e_from_mag(1, rad_45),
                sin_45)

    def test_get_obs_h_from_geo(self):
        assert_equals(self.channel.get_obs_h_from_geo(2, rad_45),
                2 * tan_45)

    def test_get_obs_h_from_mag(self):
        assert_equals(self.channel.get_obs_h_from_mag(1, rad_45),
                cos_45)
