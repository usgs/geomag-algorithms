#! /usr/bin/env python

import numpy
from nose.tools import assert_equals, assert_sequence_equal
from nose.tools import assert_almost_equal
import ChannelConverter as channel


deg2rad = numpy.pi / 180

cos_30 = numpy.cos(30 * deg2rad)
cos_45 = numpy.cos(45 * deg2rad)
cos_60 = numpy.cos(60 * deg2rad)
sin_30 = numpy.sin(30 * deg2rad)
sin_45 = numpy.sin(45 * deg2rad)
sin_60 = numpy.sin(60 * deg2rad)
tan_22pt5 = numpy.tan(22.5 * deg2rad)
tan_30 = numpy.tan(30 * deg2rad)
tan_45 = numpy.tan(45 * deg2rad)
tan_60 = numpy.tan(60 * deg2rad)
dec_bas_rad = 552.7 * numpy.pi / 60.0 / 180.0


class ChannelConverterTest:
    """Unit Tests for ChannelConverter

    Notes
    _____

    X is the northern component, Y is the eastern component.
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
        assert_almost_equal(geo_X, 1, 8,
            'Expect X to almost equal 1.')
        assert_almost_equal(geo_Y, 1, 8,
            'Expect Y to almost equal 1.')
        # Test 2
        (geo_X, geo_Y) = channel.get_geo_from_obs(1, tan_22pt5,
                22.5 * deg2rad)
        assert_almost_equal(geo_X, geo_Y, 8, 'Expect X,Y to be equal.')
        # Test 3
        (geo_X, geo_Y) = channel.get_geo_from_obs(1, 0, numpy.pi * 1.75)
        assert_almost_equal(geo_X, -geo_Y, 8,
            'Expect X,-Y to be almost equal.')
        # Test 4
        (geo_X, geo_Y) = channel.get_geo_from_obs(1, tan_30)
        assert_equals(geo_X, 1, 'Expect X to equal 1.')
        assert_equals(geo_Y, tan_30, 'Expect Y to equal tan(30).')
        # Test 5
        (geo_X, geo_Y) = channel.get_geo_from_obs(cos_30, sin_30, 30 * deg2rad)
        assert_equals(geo_X, cos_60)
        assert_equals(geo_Y, sin_60, 'Expect Y to equal sin(60).')

    def test_get_geo_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_from_mag()

        Call get_geo_from_mag using H,D of 1, 45 degrees. Expect
            X,Y to be cos_45, sin_45.
        """
        assert_sequence_equal(channel.get_geo_from_mag(1, 45 * deg2rad),
                (cos_45, sin_45), 'Expect X,Y to be cos(45), sin(45).')

    def test_get_geo_x_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_x_from_mag()

        Call get_geo_x_from_mag using H,D of 1, 45 degrees. Expect
            X to be cos_45.
        """
        assert_equals(channel.get_geo_x_from_mag(1, 45 * deg2rad),
            cos_45, 'Expect X to be cos(45).')

    def test_get_geo_y_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_mag()

        Call get_geo_y_from_mag using H,D of 1, 45 degrees. Expect
            Y to be sin_45.
        """
        assert_equals(channel.get_geo_y_from_mag(1, 45 * deg2rad),
            sin_45, 'Expect Y to be sin(45).')

    def test_get_mag_from_obs(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_obs()

        Call get_mag_from_obs using h,d of 1,0 and d0 of 45 degrees.
            Expect X,Y to equal 1,45 degrees. This is the simple case
            where the observatory values align with magnetic north
        """
        assert_sequence_equal(channel.get_mag_from_obs(1, 0, 45 * deg2rad),
            (1, 45 * deg2rad), 'Expect X,Y to be 1,45 degrees.')

    def test_get_mag_from_geo(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_obs()

        Call get_mag_from_geo using X,Y equal to each other.
            Expect H to be the hypotenuse of X,Y, and D to
            be 45 degrees.
        """
        assert_sequence_equal(channel.get_mag_from_geo(1, 1),
            (numpy.hypot(1, 1), 45 * deg2rad),
            'Expect H to be hypotenuse(1,1) and D to equal 45 degrees.')

    def test_get_mag_d_from_obs(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_obs()

        Call get_mag_d_from_obs using h,e equal to each other,
            Expect D to be 45 degrees.
        """
        assert_equals(channel.get_mag_d_from_obs(2, 2), 45 * deg2rad,
            'Expect D to be 45 degrees.')

    def test_get_mag_d_from_geo(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_geo()

        Call get_mag_d_from_geo using equal X,Y values. Expect
            D to be 45 degrees.
        """
        assert_equals(channel.get_mag_d_from_geo(2, 2), 45 * deg2rad,
            'Expect D to be 45 degrees.')

    def test_get_mag_h_from_obs(self):
        """geomag.ChannelConverterTest.test_get_mag_h_from_obs()

        Call get_mag_h_from_obs using h,e of 3,4. Expect H to be 5.
        """
        assert_equals(channel.get_mag_h_from_obs(3, 4), 5,
            'Expect H to be 5.')

    def test_get_mag_h_from_geo(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_geo()

        Call get_mag_h_from_geo using X,Y of 3,4. Expect H to be 5.
        """
        assert_equals(channel.get_mag_h_from_geo(3, 4), 5,
            'Expect H to be 5.')

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
        assert_almost_equal(obs_h, 1.0, 8, 'Expect h to be 1.')
        assert_almost_equal(obs_e, 1.0, 8, 'Expect e to be 1.')
        # Test 2
        (obs_h, obs_e) = channel.get_obs_from_geo(1, 1, 22.5 * deg2rad)
        d = channel.get_obs_d_from_obs(obs_h, obs_e)
        assert_equals(d, 22.5 * deg2rad, 'Expect d to be 22.5 degrees.')
        # Test 3
        (obs_h, obs_e) = channel.get_obs_from_geo(1, 1, numpy.pi * 1.75)
        d = channel.get_obs_d_from_obs(obs_h, obs_e)
        assert_almost_equal(d, 90 * deg2rad, 8, 'Expect d to be 90 degrees.')
        # Test 4
        (obs_h, obs_e) = channel.get_obs_from_geo(cos_60, sin_60, 30 * deg2rad)
        assert_equals(obs_h, cos_30, 'Expect h to be cos(30).')
        assert_equals(obs_e, sin_30, 'Expect e to be sin(30).')
        assert_equals(channel.get_obs_d_from_obs(obs_h, obs_e), 30 * deg2rad)

    def test_get_obs_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_from_mag()

        Call the get_obs_from_mag function, using trig identities too
        test correctness, including d0. Which should test most of the d0
        calls.
        The second value (obs_e) is off in the 18th place probably due to
        computing errors.
        """
        (obs_h, obs_e) = channel.get_obs_from_mag(1, -22.5 * deg2rad,
            22.5 * deg2rad)
        assert_equals(obs_h, cos_45, 'Expect h to be cos(45)')
        assert_almost_equal(obs_e, -cos_45, 8, 'Expect e to be -cos(45).')

    def test_get_obs_d_from_obs(self):
        """geomag.ChannelConverterTest.test_get_obs_d_from_obs()

        Call get_obs_d_from_obs using equal values for h,e. Expect
            d to be 45.
        """
        assert_equals(channel.get_obs_d_from_obs(1, 1),
                45 * deg2rad, 'Expect d to be 45 degrees.')

    def test_get_obs_d_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_d_from_mag()

        1) Call get_obs_d_from_mag using d = 1, expect observatory declination
            of 1 back.
        2) Call get_obs_d_from_mag using d, d0 values of 22.5, 45 expect
            observatory declination of -22.5 degrees.
        """
        assert_equals(channel.get_obs_d_from_mag(1), 1,
            'Expect d to be 1.')
        assert_equals(channel.get_obs_d_from_mag(22.5 * deg2rad, 45 * deg2rad),
            -22.5 * deg2rad, 'Expect d to be -22.5 degrees.')

    def test_get_obs_e_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_e_from_mag()

        Call get_obs_e_from mag using H,D of 1,45.  Expect e to be sin(45)
        """
        assert_equals(channel.get_obs_e_from_mag(1, 45 * deg2rad),
                sin_45, 'Expect e to be sin(45).')

    def test_get_obs_e_from_obs(self):
        """geomag.ChannelConverterTest.test_get_obs_e_from_obs()

        Call get_obs_e_from_obs using h,d of 2, 45. Expect e to be 2 * tan(45)
        """
        assert_equals(channel.get_obs_e_from_obs(2, 45 * deg2rad),
                2 * tan_45, 'Expect e to be 2 * tan(45).')

    def test_get_obs_h_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_h_from_mag()

        Call get_obs_h_from_mag using H,D 1,45. expect h to be cos(45)
        """
        assert_equals(channel.get_obs_h_from_mag(1, 45 * deg2rad),
                cos_45, 'Expect h to be cos(45).')

    def test_geo_to_obs_to_geo(self):
        """geomag.ChannelConverterTest.test_geo_to_obs_to_geo()

        Call get_geo_from_obs using values from Boulder, then call
            get_obs_from_geo using the X,Y values returned from
            get_geo_from_obs. Expect the end values to be the same.
        """
        (geo_X, geo_Y) = channel.get_geo_from_obs(20840.15, -74.16,
            dec_bas_rad)
        (obs_h, obs_e) = channel.get_obs_from_geo(geo_X, geo_Y, dec_bas_rad)

        assert_almost_equal(obs_h, 20840.15, 8, 'Expect h to = 20840.15.')
        assert_almost_equal(obs_e, -74.16, 8, 'Expect e to = -74.16')
