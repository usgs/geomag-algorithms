#! /usr/bin/env python

import numpy
import math
import ChannelConverter as channel

assert_equals = numpy.testing.assert_equal
assert_almost_equal = numpy.testing.assert_almost_equal
cos = math.cos
sin = math.sin
tan = math.tan

D2R = numpy.pi / 180

dec_bas_rad = 552.7 * numpy.pi / 60.0 / 180.0


class ChannelConverterTest:
    """Unit Tests for ChannelConverter

    Notes
    _____

    Observatory frame of reference.
        h: the component corresponding to the field strength along the
            observatories primary horizontal axis.
        e: the component corresponding to the field strength along the
            observatories secondary horizonal axis.
        d: the angle between observatory h and the horizontal field value
            (aka magnetic north in the horizontal plane.)
        d0: the declination baseline angle of the observatory as originally
            set up.
    Magnetic frame of reference.
        H: the horizontal vector corresponding to the field strength along
            magnetic north.
        D: the declination or clockwise angle from the vector pointing to
            the geographic north pole to the H vector.
    Geographic frame of reference.
        X: the component corresponding to the field strength along
            geographic north.
        Y: the component corresponding to the field strength along
            geographic east.

    We are using triangle identities for variables to test with.  Specifically
        the hypotenuse is normally equal to 1, causing the adjacent angle
        length to be cos(angle) and the opposite length to be sin(angle)
    """

    def test_get_geo_from_obs(self):
        """geomag.ChannelConverterTest.test_get_geo_from_obs()

        The observatory component ``h`` and ``e`` combined with the declination
        basline angle ``d0`` converts to the geographic north component
        ``X`` and east vector ``Y``
        """

        # 1) Call get_geo_from_obs using equal h,e values with a d0 of 0
        #   the geographic values X,Y will be the same. This proves the simple
        #   case where the observatory is aligned with geographic north.
        h = 1
        e = 1
        (X, Y) = channel.get_geo_from_obs(h, e)
        assert_almost_equal(X, 1, 8, 'Expect X to almost equal 1.', True)
        assert_almost_equal(Y, 1, 8, 'Expect Y to almost equal 1.', True)

        # 2) Call get_geo_from_obs using h,e values of cos(15), sin(15)
        #       (to create a d of 15 degrees) and a d0 of 15 degrees.
        #       X and Y will be cos(30), sin(30)
        h = cos(15 * D2R)
        e = sin(15 * D2R)
        d0 = 15 * D2R
        (X, Y) = channel.get_geo_from_obs(h, e, d0)
        assert_equals(X, cos(30 * D2R), 'Expect X to equal cos(30)', True)
        assert_equals(Y, sin(30 * D2R), 'Expect Y to equal sin(30)', True)

        # 3) Call get_geo_from_obs using h,e values of 1,0 with a d0 of 315
        #   degrees. The geographic X,Y will be cos(45), sin(-45)
        h = 1
        e = 0
        d0 = 315 * D2R
        (X, Y) = channel.get_geo_from_obs(h, e, d0)
        assert_almost_equal(X, cos(45 * D2R), 8,
                'Expect X to equal cos(45).', True)
        assert_almost_equal(Y, sin(-45 * D2R), 8,
                'Expect Y to equal sin(45).', True)

        # 4) Call get_geo_from_obs using h,e values of cos_30,sin_30 and d0 of
        #   30 degrees. The geographic X,Y will be cos(-30), sin(-30), due to
        #   combined angle of the observatory declination of 30 degrees, and
        #   the d0 of -60 degrees.
        h = cos(30 * D2R)
        e = sin(30 * D2R)
        d0 = -60 * D2R
        (X, Y) = channel.get_geo_from_obs(h, e, d0)
        assert_equals(X, cos(-30 * D2R), 'Expect X to equal cos(60).', True)
        assert_equals(Y, sin(-30 * D2R), 'Expect Y to equal sin(60).', True)

    def test_get_geo_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_from_mag()

        ``X``, ``Y`` are the north component, and east component of the
        vector ``H`` which is an angle ``D`` from north.
        """

        # Call get_geo_from_mag using H,D of 1, 45 degrees. Expect
        #   X, Y to be cos_45, sin_45.
        h = 1
        d = 30 * D2R
        (X, Y) = channel.get_geo_from_mag(h, d)
        assert_equals(X, cos(30 * D2R), 'Expect X to be cos(30).', True)
        assert_equals(Y, sin(30 * D2R), 'Expect Y to be sin(30).', True)

    def test_get_geo_x_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_x_from_mag()

        ``X`` is the north component of the vector ``H``, which is an angle
        ``D`` from north.
        """

        # 1) Call get_geo_x_from_mag using H,D of 1, 45 degrees. Expect
        #    X to be cos(45).
        h = 2
        d = 45 * D2R
        X = channel.get_geo_x_from_mag(h, d)
        assert_equals(X, 2 * cos(d), 'Expect X to be cos(45).', True)
        # 2) Call get_geo_x_from_mag using H,D of 1, 30 degrees. Expect
        #   X to be cos(30)
        h = 2
        d = 30 * D2R
        X = channel.get_geo_x_from_mag(h, d)
        assert_equals(X, 2 * cos(d), 'Expect X to equal cos(30).', True)

    def test_get_geo_y_from_mag(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_mag()

        ``Y`` is the north component of the vector ``H``, which is an angle
        ``D`` from north.
        """

        # 1) Call get_geo_y_from_mag using H,D of 1, 45 degrees. Expect
        #   Y to be sin_45.
        h = 2
        d = 45 * D2R
        Y = channel.get_geo_y_from_mag(h, d)
        assert_equals(Y, 2 * sin(45 * D2R), 'Expect Y to be 2sin(45).', True)
        # 2) Call get_geo_x_from_mag using H,D of 1, 30 degrees. Expect
        #   X to be cos(30)
        h = 2
        d = 30 * D2R
        Y = channel.get_geo_y_from_mag(h, d)
        assert_equals(Y, 2 * sin(30 * D2R), 'Expect Y to be 2sin(30).', True)

    def test_get_mag_from_obs(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_obs()

        ``h``, ``e`` are the primary and secondary axis of the ``H``
        vector in the horizontal plane of the magnetic field.  ``d0``
        is the declination baseline of the observatory frame of reference.
        ``D`` comes from the combination of ``d0`` and the angle produced
        from the ``h`` and ``e`` components.
        """

        # Call get_mag_from_obs using h,d of cos(30), sin(30) and
        #   d0 of 15 degrees. Expect H,D to equal 1, 45.
        h = cos(30 * D2R)
        e = sin(30 * D2R)
        d0 = 15 * D2R
        H, D = channel.get_mag_from_obs(h, e, d0)
        assert_equals(H, 1, 'Expect H to be 1.', True)
        assert_equals(D, 45 * D2R, 'Expect D to be 45.', True)

    def test_get_mag_from_geo(self):
        """geomag.ChannelConverterTest.test_get_geo_y_from_obs()

        ``X`` and ``Y are the north and east components of the ``H`` total
        magnetic field horizontal vector.  ``D`` is the angle from north of
        that vector.
        """

        # Call get_mag_from_geo using X,Y of 3cos(30), 3sin(30).
        #    Expect H to be 3, and D to be 30 degrees.
        X = 3 * cos(30 * D2R)
        Y = 3 * sin(30 * D2R)
        H, D = channel.get_mag_from_geo(X, Y)
        assert_equals(H, 3, 'Expect H to equal 3.', True)
        assert_equals(D, 30 * D2R, 'Expect D to be 30.', True)

    def test_get_mag_d_from_obs(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_obs()

        The observatory components ``h`` and ``e`` form an angle (d) with
        the horizontal magnetic vector. Adding d to the observatory
        declination baseline ``d0`` the magnetic declination angle ``D`` can
        be found.
        """

        # 1) Call get_mag_d_from_obs using h,e equal to each other.
        #   Expect D to be 45 degrees.
        h = 2
        e = 2
        D = channel.get_mag_d_from_obs(h, e)
        assert_equals(D, 45 * D2R, 'Expect D to be 45 degrees.', True)
        # 2) Call get_mag_d_from_obs using h,e cos(30), sin(30).
        #   Expect d of 30 degress.
        h = cos(30 * D2R)
        e = sin(30 * D2R)
        D = channel.get_mag_d_from_obs(h, e)
        assert_equals(D, 30 * D2R, 'Expect D to equal 30 degrees', True)
        # 3) Call get_mag_d_from_obs using h,e cos(30), sin(30),
        #   d0 = 30 degrees Expect d to be 60 degress.
        h = cos(30 * D2R)
        e = sin(30 * D2R)
        d0 = 30 * D2R
        D = channel.get_mag_d_from_obs(h, e, d0)
        assert_equals(D, 60 * D2R, 'Expect D to equal 60 degrees', True)
        # 4) Call get_mag_d_from_obs using h,e cos(30), sin(30),
        #   d0 = 330 degrees Expect d of 360 degress.
        h = cos(30 * D2R)
        e = sin(30 * D2R)
        d0 = 330 * D2R
        D = channel.get_mag_d_from_obs(h, e, d0)
        assert_equals(D, 360 * D2R, 'Expect D to equal 360 degrees', True)
        # 5) Call get_mag_d_from_obs using h,e cos(30), sin(30),
        #   d0 = -30 degrees Expect d of 0 degress.
        h = cos(30 * D2R)
        e = sin(30 * D2R)
        d0 = -30 * D2R
        D = channel.get_mag_d_from_obs(h, e, d0)
        assert_equals(D, 0, 'Expect D to equal 0 degrees', True)
        # 6) Call get_mag_d_from_obs using h,e cos(30), -sin(30),
        #   d0 = -30 degrees. Expect d of -60 degress.
        h = cos(30 * D2R)
        e = sin(-30 * D2R)
        d0 = -30 * D2R
        D = channel.get_mag_d_from_obs(h, e, d0)
        assert_equals(D, -60 * D2R, 'Expect D to equal -60 degrees', True)

    def test_get_mag_d_from_geo(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_geo()

        Angle ``D`` from north of the horizontal vector can be calculated
        using the arctan of the ``X`` and ``Y`` components.
        """

        # 1) Call get_mag_d_from_geo using equal X,Y values. Expect
        #   D to be 45 degrees.
        X = 2
        Y = 2
        D = channel.get_mag_d_from_geo(X, Y)
        assert_equals(D, 45 * D2R, 'Expect D to be 45 degrees.', True)
        # 2) Call get_mag_d_from_geo using X,Y equal to cos(30), sin(30).
        #   Expect D to be 30 degrees.
        X = cos(30 * D2R)
        Y = sin(30 * D2R)
        D = channel.get_mag_d_from_geo(X, Y)
        assert_equals(D, 30 * D2R, 'Expect D to be 30 degrees.', True)
        # 3) Call get_mag_d_from_geo using X,Y equal to cos(30), -sin(30).
        #   Expect D to be -30 degrees.
        X = cos(30 * D2R)
        Y = sin(-30 * D2R)
        D = channel.get_mag_d_from_geo(X, Y)
        assert_equals(D, -30 * D2R, 'Expect D to equal -30 degrees', True)

    def test_get_mag_h_from_obs(self):
        """geomag.ChannelConverterTest.test_get_mag_h_from_obs()

        ``h`` and ``e`` are the primary and secondary components of the ``H``
        vector.
        """

        # Call get_mag_h_from_obs using h,e of 3,4. Expect H to be 5.
        h = 3
        e = 4
        H = channel.get_mag_h_from_obs(h, e)
        assert_equals(H, 5, 'Expect H to be 5.', True)

    def test_get_mag_h_from_geo(self):
        """geomag.ChannelConverterTest.test_get_mag_d_from_geo()

        ``X`` and ``Y`` are the north and east components of the horizontal
        magnetic field vector ``H``
        """

        # Call get_mag_h_from_geo using X,Y of 3,4. Expect H to be 5.
        X = 3
        Y = 4
        H = channel.get_mag_h_from_geo(X, Y)
        assert_equals(H, 5, 'Expect H to be 5.', True)

    def test_get_obs_from_geo(self):
        """geomag.io.channelTest.test_get_obs_from_geo()

        The geographic north and east components ``X`` and ``Y`` of the
        magnetic field vector H, combined with the declination baseline angle
        ``d0`` can be used to produce the observatory components ``h`` and
        ```e``
        """

        # 1) Call get_obs_from_geo using equal X,Y values with a d0 of 0
        #   the observatory values h,e will be the same.
        X = 1
        Y = 1
        (h, e) = channel.get_obs_from_geo(X, Y)
        assert_almost_equal(h, 1.0, 8, 'Expect h to be 1.', True)
        assert_almost_equal(e, 1.0, 8, 'Expect e to be 1.', True)
        # 2) Call get_obs_from_geo using equal X,Y values to create a 45
        #   degree angle (D), with a d0 of 45/2. The observatory declination
        #   (d) will be 45/2, the difference between the total field angle,
        #   and d0.
        X = 1
        Y = 1
        d0 = 22.5 * D2R
        (h, e) = channel.get_obs_from_geo(X, Y, d0)
        d = channel.get_obs_d_from_obs(h, e)
        assert_equals(d, 22.5 * D2R, 'Expect d to be 22.5 degrees.', True)
        # 3) Call get_obs_from_geo using equal X,Y values to create a 45
        #   degree angle (D), with a d0 of 315 degrees. The observatory
        #   declination (d) will be 90 degrees.
        X = 1
        Y = 1
        d0 = 315 * D2R
        (h, e) = channel.get_obs_from_geo(X, Y, d0)
        d = channel.get_obs_d_from_obs(h, e)
        assert_almost_equal(d, 90 * D2R, 8, 'Expect d to be 90 degrees.', True)
        # 4) Call get_obs_from_geo using X,Y values of cos(60), sin(60), and
        #   d0 of 30 degrees. The observatory values h,e will be cos(30)
        #   and sin(30), and the observatory declination will be 30 degrees.
        #   The observatory angle of 30 degrees + the d0 of 30 degrees produces
        #   the total declination (D) of 60 degrees.
        X = cos(60 * D2R)
        Y = sin(60 * D2R)
        d0 = 30 * D2R
        (h, e) = channel.get_obs_from_geo(X, Y, d0)
        assert_equals(h, cos(30 * D2R), 'Expect h to be cos(30).', True)
        assert_equals(e, sin(30 * D2R), 'Expect e to be sin(30).', True)
        d = channel.get_obs_d_from_obs(h, e)
        assert_equals(d, 30 * D2R, 'Expect d to be 30 degrees.', True)

    def test_get_obs_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_from_mag()

        Call the get_obs_from_mag function, using trig identities too
        test correctness, including d0. Which should test most of the d0
        calls.
        """

        H = 1
        D = -22.5 * D2R
        (h, e) = channel.get_obs_from_mag(H, D, 22.5 * D2R)
        assert_equals(h, cos(45 * D2R), 'Expect h to be cos(45)', True)
        assert_almost_equal(e, -cos(45 * D2R), 8,
                'Expect e to be -cos(45).', True)

    def test_get_obs_d_from_obs(self):
        """geomag.ChannelConverterTest.test_get_obs_d_from_obs()

        ``d`` is the angle formed by the observatory components ``h`` and
        ``e`` the primary and secondary axis of the horizontal magnetic
        field vector in the observatories frame of reference.
        """
        # 1) Call get_obs_d_from_obs usine h,e equal to cos(30), sin(30).
        #   Expect d to be 30.
        h = cos(30 * D2R)
        e = sin(30 * D2R)
        d = channel.get_obs_d_from_obs(h, e)
        assert_equals(d, 30 * D2R, 'Expect d to be 30 degrees.', True)
        # 2) Call get_obs_d_from_obs using h,e cos(30), -sin(30). Expect
        #   d to be 30.
        h = cos(30 * D2R)
        e = sin(-30 * D2R)
        d = channel.get_obs_d_from_obs(h, e)
        assert_equals(d, -30 * D2R, 'Expect d to be 30 degrees.', True)

    def test_get_obs_d_from_mag_d(self):
        """geomag.ChannelConverterTest.test_get_obs_d_from_mag()

        The observatory declination angle ``d`` is the difference between
        the magnetic north declination ``D`` and the observatory baseline
        declination angle ``d0``.
        """

        # 1) Call get_obs_d_from_mag using D = 1. Expect observatory
        #   declination of 1 back.
        D = 1
        d = channel.get_obs_d_from_mag_d(D)
        assert_equals(d, 1, 'Expect d to be 1.', True)
        # 2) Call get_obs_d_from_mag using d, d0 values of 22.5, 45. Expect
        #   observatory declination of -22.5 degrees.
        D = 22.5 * D2R
        d0 = 45 * D2R
        d = channel.get_obs_d_from_mag_d(D, d0)
        assert_equals(d, -22.5 * D2R, 'Expect d to be -22.5 degrees.', True)
        # 3) Call get_obs_d_from_mag using d, d0 values of 60, 30. Expect
        #   observatory declination of 30 degrees.
        D = 60 * D2R
        d0 = 30 * D2R
        d = channel.get_obs_d_from_mag_d(D, d0)
        assert_equals(d, 30 * D2R, 'Expect d to be 30 degrees.', True)
        # 4) Call get_obs_d_from_mag using d, d0 values of 30, -30.
        #   Expect observatory declination of 60 degrees.
        D = 30 * D2R
        d0 = -30 * D2R
        d = channel.get_obs_d_from_mag_d(D, d0)
        assert_equals(d, 60 * D2R, 'Expect d to be 60 degrees.', True)

    def test_get_obs_e_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_e_from_mag()

        ``e`` is the secondary axis or 'east' component of the observatory
        reference frame. Using the difference between the magnetic declination
        angle ``D`` and the observatory baseline declination ``d0`` to get the
        observatory declination angle d the ``e`` component can be found
        as ``H`` * sin(d)
        """

        # 1) Call get_obs_e_from mag using H,D of 1,45.  Expect e to be sin(45)
        H = 1
        D = 45 * D2R
        e = channel.get_obs_e_from_mag(H, D)
        assert_equals(e, sin(45 * D2R), 'Expect e to be sin(45).', True)
        # 2) Call get_obs_e_from_mag using H,D of 1, 30. Expect e to be sin(30)
        H = 1
        D = 30 * D2R
        e = channel.get_obs_e_from_mag(H, D)
        assert_equals(e, sin(30 * D2R), 'Expect e to be sin(30).', True)
        # 3) Call get_obs_e_from_mag using H,D,d0 of 1, 15, -15. Expect e to
        #   be sin(30)
        H = 1
        D = 15 * D2R
        d0 = -15 * D2R
        e = channel.get_obs_e_from_mag(H, D, d0)
        assert_equals(e, sin(30 * D2R), 'Expect e to be sin(30)', True)

    def test_get_obs_e_from_obs(self):
        """geomag.ChannelConverterTest.test_get_obs_e_from_obs()

        ``e`` is the seconday (east) component of the observatory vector ``h``.
        ``e`` is calculated using ``h`` * tan(``d``) where ``d`` is the
        declination angle of the observatory.
        """

        # Call get_obs_e_from_obs using h,d of 2, 30.
        #   Expect e to be 2 * tan(30)
        h = 2
        d = 30 * D2R
        e = channel.get_obs_e_from_obs(h, d)
        assert_equals(e, 2 * tan(30 * D2R),
                'Expect e to be 2 * tan(30).', True)

    def test_get_obs_h_from_mag(self):
        """geomag.ChannelConverterTest.test_get_obs_h_from_mag()

        The observatories horizontal magnetic vector ``h`` is caculated from
        the magnetic north vector ``H`` and the observatory declination angle
        ``d``.  ``d`` is the difference of the magnetic declination ``D`` and
        the observatory baseline declination ``d0``
        """

        # 1) Call get_obs_h_from_mag using H,D 1,45. Expect h to be cos(45)
        H = 1
        D = 45 * D2R
        h = channel.get_obs_h_from_mag(H, D)
        assert_equals(h, cos(45 * D2R), 'Expect h to be cos(45).', True)
        # 2) Call get_obs_h_from_mag using H,D,d0 1,30,15.
        #   Expect h to be cos(15)
        H = 1
        D = 30 * D2R
        d0 = 15 * D2R
        h = channel.get_obs_h_from_mag(H, D, d0)
        assert_equals(h, cos(15 * D2R), 'Expect h to be cos(15)', True)

    def test_geo_to_obs_to_geo(self):
        """geomag.ChannelConverterTest.test_geo_to_obs_to_geo()

        Call get_geo_from_obs using values from Boulder, then call
            get_obs_from_geo using the X,Y values returned from
            get_geo_from_obs. Expect the end values to be the same
            as the start values.
        """
        h_in = 20840.15
        e_in = -74.16
        d0 = dec_bas_rad
        (X, Y) = channel.get_geo_from_obs(h_in, e_in, d0)
        (h, e) = channel.get_obs_from_geo(X, Y, d0)

        assert_almost_equal(h, 20840.15, 8, 'Expect h to = 20840.15.', True)
        assert_almost_equal(e, -74.16, 8, 'Expect e to = -74.16', True)

    def test_get_radians_from_minutes(self):
        """geomag.ChannelConverterTest.test_get_radian_from_decimal()

        Call get_radian_from_decimal using 45 degrees, expect r to be pi/4
        """
        minutes = 45 * 60
        radians = channel.get_radians_from_minutes(minutes)
        assert_equals(radians, math.pi / 4.0,
                'Expect radians to be pi/4', True)

    def test_get_minutes_from_radians(self):
        """geomag.ChannelConverterTest.test_get_decimal_from_radian()

        Call get_decimal_from_radian using pi/4, expect d to be 45
        """
        radians = math.pi / 4.0
        minutes = channel.get_minutes_from_radians(radians)
        assert_equals(minutes, 45 * 60,
                'Expect minutes to be equal to 45 degrees', True)
