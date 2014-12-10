#! /usr/bin/env python

import numpy
from nose.tools import assert_equals, assert_sequence_equal
from nose.tools import assert_almost_equal
import ChannelConverter as channel


deg2rad = numpy.pi / 180
rad_half_45 = numpy.pi / 8
rad_30 = numpy.pi / 6
rad_45 = numpy.pi / 4
cos_30 = numpy.cos(numpy.pi / 6)
cos_45 = numpy.cos(numpy.pi / 4)
cos_60 = numpy.cos(numpy.pi / 3)
sin_30 = numpy.sin(numpy.pi / 6)
sin_45 = numpy.sin(numpy.pi / 4)
sin_60 = numpy.sin(numpy.pi / 3)
tan_22pt5 = numpy.tan(22.5 * deg2rad)
tan_30 = numpy.tan(numpy.pi / 6)
tan_45 = numpy.tan(numpy.pi / 4)
tan_60 = numpy.tan(numpy.pi / 3)
dec_base_rad = 552.7 * numpy.pi / 60.0 / 180.0


class ChannelConverterTest:
    """Unit Tests for ChannelConverter

    Notes
    _____

    Doing multiple tests in test_geo_geo_from_obs, as this tests all
        the obs to mag, and mag to geo routines.
    Also doing multiple tests in test_get_obs_from_geo as this will test
        the reverse tests.
    """

    def test_get_geo_from_obs(self):
        """geomag.ChannelConverterTest.test_get_geo_from_obs()

        1) Call get_geo_from_obs using equal h,e values with a d0 of 0
            the geographic values X,Y will be the same.
        2) Call get_geo_from_obs using h,e values of 1,tan(45/2) with d0 of
            45/2.  The geographic values X,Y will be 1,1, since the observatory
            declination + d0 angle will produce a 45 degree angle.
        3) Call get_geo_from_obs using h,e values of 1,0 with a d0 of 315
            degrees. The geographic X,Y will be 1,-1. Since the obs will be
            in line with magnetic north, at -45 degrees.
        4) Call get_geo_from_obs using h,e values of 1,tan(30) with d0 of 0.
            X,Y will be 1, tan(30). The observatory and the geographic values
            are equal since the observatory is aligned with geographic north.
        5) Call get_geo_from_obs using h,e values of cos_30,sin_30 and d0 of
            30 degrees. The geographic X,Y will be cos_60, sin_60, due to
            combined angle of the observatory declination of 30 degrees, and
            the d0 of 30 degrees.
        """
        # Test 1
        (geo_X, geo_Y) = channel.get_geo_from_obs(1, 1)
        assert_almost_equal(geo_X, 1)
        assert_almost_equal(geo_Y, 1)
        # Test 2
        (geo_X, geo_Y) = channel.get_geo_from_obs(1, tan_22pt5,
                22.5 * deg2rad)
        assert_almost_equal(geo_X, geo_Y, places=8)
        # Test 3
        (geo_X, geo_Y) = channel.get_geo_from_obs(1, 0, numpy.pi * 1.75)
        assert_almost_equal(geo_X, -geo_Y, places=8)
        # Test 4
        (geo_X, geo_Y) = channel.get_geo_from_obs(1, tan_30)
        assert_equals(geo_X, 1)
        assert_equals(geo_Y, tan_30)
        # Test 5
        (geo_X, geo_Y) = channel.get_geo_from_obs(cos_30, sin_30, rad_30)
        assert_equals(geo_X, cos_60)
        assert_almost_equal(geo_Y, sin_60, places=8)

    def test_get_geo_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_from_mag()

        Call get_geo_from_mag using H,D of 1, 45 degrees. Expect
            X,Y to be cos_45, sin_45.
        """
        assert_sequence_equal(channel.get_geo_from_mag(1, 45 * deg2rad),
                (cos_45, sin_45))

    def test_get_geo_x_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_x_from_mag()

        Call get_geo_x_from_mag using H,D of 1, 45 degrees. Expect
            X to be cos_45.
        """
        assert_equals(channel.get_geo_x_from_mag(1, 45 * deg2rad),
            cos_45)

    def test_get_geo_y_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_mag()

        Call get_geo_y_from_mag using H,D of 1, 45 degrees. Expect
            Y to be sin_45.
        """
        assert_equals(channel.get_geo_y_from_mag(1, 45 * deg2rad),
            sin_45)

    def test_get_mag_from_obs(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_obs()

        Call get_mag_from_obs using h,d of 1,0 and d0 of rad_45.
            Expect X,Y to equal 1,rad_45. This is the simple case
            where the observatory values align with magnetic north
        """
        assert_sequence_equal(channel.get_mag_from_obs(1, 0, 45 * deg2rad),
            (1, 45 * deg2rad))

    def test_get_mag_from_geo(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_obs()

        Call get_mag_from_geo using X,Y equal to each other.
            Expect H to be the hypotenuse of X,Y, and D to
            be 45 degrees.
        """
        assert_sequence_equal(channel.get_mag_from_geo(1, 1),
            (numpy.hypot(1, 1), 45 * deg2rad))

    def test_get_mag_d_from_obs(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_obs()

        Call get_mag_d_from_obs using h,e equal to each other,
            Expect D to be 45 degrees.
        """
        assert_equals(channel.get_mag_d_from_obs(2, 2), 45 * deg2rad)

    def test_get_mag_d_from_geo(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_geo()

        Call get_mag_d_from_geo using equal X,Y values. Expect
            D to be 45 degrees.
        """
        assert_equals(channel.get_mag_d_from_geo(2, 2), 45 * deg2rad)

    def test_get_mag_h_from_obs(self):
        """geomag.ChannelConverterTest.test_get_mag_h_from_obs()

        Call get_mag_h_from_obs using h,e of 3,4. Expect H to be 5.
        """
        assert_equals(channel.get_mag_h_from_obs(3, 4), 5)

    def test_get_mag_h_from_geo(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_geo()

        Call get_mag_h_from_geo using X,Y of 3,4. Expect H to be 5.
        """
        assert_equals(channel.get_mag_h_from_geo(3, 4), 5)

    def test_get_obs_from_geo(self):
        """geomag.io.channelTest.test_get_obs_from_geo()

        1) Call get_obs_from_geo using equal X,Y values with a d0 of 0
            the observatory values h,e will be the same.
        2) Call get_obs_from_geo using equal X,Y values to create a 45
            degree angle (D), with a d0 of 45/2. The observatory declination
            (d) will be 45/2, the difference between the total field angle,
            and d0.
        3) Call get_obs_from_geo using equal X,Y values to create a 45
            degree angle (D), with a d0 of 315 degrees. The observatory
            declination (d) will be 90 degrees.
        4) Call get_obs_from_geo using X,Y values of cos_60, sin60, and
            d0 of 30 degrees. The observatory values h,e will be cos_30
            and sin_30, and the observatory declination will be 30 degrees.
            The observatory angle of 30 degrees + the d0 of 30 degrees produces
            the total declination (D) of 60 degrees.
        """
        # Test 1
        (obs_h, obs_e) = channel.get_obs_from_geo(1, 1)
        assert_almost_equal(obs_h, 1.0, places=8)
        assert_almost_equal(obs_e, 1.0, places=8)
        # Test 2
        (obs_h, obs_e) = channel.get_obs_from_geo(1, 1, 22.5 * deg2rad)
        d = channel.get_obs_d_from_obs(obs_h, obs_e)
        assert_equals(d, 22.5 * deg2rad)
        # Test 3
        (obs_h, obs_e) = channel.get_obs_from_geo(1, 1, numpy.pi * 1.75)
        d = channel.get_obs_d_from_obs(obs_h, obs_e)
        assert_almost_equal(d, 90 * deg2rad)
        # Test 4
        (obs_h, obs_e) = channel.get_obs_from_geo(cos_60, sin_60, rad_30)
        assert_equals(obs_h, cos_30)
        assert_equals(obs_e, sin_30)
        assert_equals(channel.get_obs_d_from_obs(obs_h, obs_e), rad_30)

    def test_get_obs_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_from_mag()

        Call the get_obs_from_mag function, using trig identities too
        test correctness, including d0. Which should test most of the d0
        calls.
        The second value (obs_e) is off in the 18th place probably due to
        computing errors.
        """
        obs = channel.get_obs_from_mag(1, -22.5 * deg2rad, 22.5 * deg2rad)
        assert_equals(obs[0], cos_45)
        assert_almost_equal(obs[1], -cos_45, places=8)

    def test_get_obs_d_from_obs(self):
        """geomag.ChannelConverterTest.test_get_obs_d_from_obs()

        Call get_obs_d_from_obs using equal values for h,e. Expect
            d to be 45.

        Call the get_obs_d_from_obs function, using trig identities too
        test correctness.

        arctan2(e, h)
        """
        assert_equals(channel.get_obs_d_from_obs(1, 1),
                45 * deg2rad)

    def test_get_obs_d_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_d_from_mag()

        1) Call get_obs_d_from_mag using d = 1, expect observatory declination
            of 1 back.
        2) Call get_obs_d_from_mag using d, d0 values of 22.5, 45 expect
            observatory declination of -22.5 degrees.
        """
        assert_equals(channel.get_obs_d_from_mag(1), 1)
        assert_equals(channel.get_obs_d_from_mag(22.5 * deg2rad, 45 * deg2rad),
            -22.5 * deg2rad)

    def test_get_obs_e_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_e_from_mag()

        Call the get_obs_e_from_mag function, using trig identities too
        test correctness.
        """
        assert_equals(channel.get_obs_e_from_mag(1, 45 * deg2rad),
                sin_45)

    def test_get_obs_e_from_obs(self):
        """geomag.ChannelConverterTest.test_get_obs_e_from_obs()

        Call the get_obs_e_from_obs function, using trig identities too
        test correctness.

        h * tan(d)
        """
        assert_equals(channel.get_obs_e_from_obs(2, 45 * deg2rad),
                2 * tan_45)

    def test_get_obs_h_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_h_from_mag()

        Call the get_obs_h_from_mag function, using trig identities too
        test correctness.
        """
        assert_equals(channel.get_obs_h_from_mag(1, 45 * deg2rad),
                cos_45)
