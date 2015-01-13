"""Unit Tests for StreamConverter

Notes
-----

We are using triangle identities for variables to test with.  Specifically
    the hypotenuse is normally equal to 1, causing the adjacent angle length
    to be cos(angle) and the opposite length to be sin(angle)

For more info on the components see the Notes in ChannelConverterTest.py.
"""
import obspy.core
import numpy
import StreamConverter
import ChannelConverter

assert_equals = numpy.testing.assert_equal
assert_almost_equals = numpy.testing.assert_almost_equal

cos = numpy.cos
sin = numpy.sin

D2R = numpy.pi / 180
D2I = 60 * 10               # Degrees to Iaga Decbas
STARTTIME = obspy.core.UTCDateTime('2014-11-01')

stats = obspy.core.Stats()
stats.comments = ""
stats.starttime = STARTTIME
stats.sampling_rate = 0.0166666666667
stats.npts = 1
stats.DECBAS = 0


def test_get_geo_from_mag():
    """geomag.StreamConverter_test.test_get_geo_from_mag()

    The magnetic north stream containing the traces ''h'', ''d'', ''z'', and
    ''f'' converts to the geographics stream containing the traces ''x'',
    ''y'', ''z'' and ''f''
    """
    mag = obspy.core.Stream()

    # Call get_geo_from_magusing a decbas of 15 degrees, and streams with
    #   H = [1, 1], and D = [15 degrees, 30 degrees], expect streams of
    #   X = [cos(15), cos(30)] and Y = [sin(15), sin(30)]
    # stats.DECBAS = 15 * D2I
    stats.npts = 2
    mag += __create_trace('H', [1, 1])
    mag += __create_trace('D', [15 * D2R, 30 * D2R])
    mag += __create_trace('Z', [1, 1])
    mag += __create_trace('F', [1, 1])
    geo = StreamConverter.get_geo_from_mag(mag)
    X = geo.select(channel='X')[0].data
    Y = geo.select(channel='Y')[0].data
    assert_equals(X, [cos(15 * D2R), cos(30 * D2R)],
        'Expect X to equal [cos(15), cos(30)]', True)
    assert_equals(Y, [sin(15 * D2R), sin(30 * D2R)],
        'Expect Y to equal [sin(15), sin(30)]', True)


def test_get_geo_from_obs():
    """geomag.StreamConverter_test.test_get_geo_from_obs()

    The observatory stream containing the observatory traces
    ''h'', ''d'' or ''e'', ''z'', and ''f'' converts to the geographic
    stream containing the traces ''x'', ''y'', ''z'', and ''f''
    """
    obs = obspy.core.Stream()

    # 1) Call get_geo_from_obs using equal h, e streams with a decbas of 0
    #   the geographic stream values X, Y will be the same.
    stats.DECBAS = 0
    stats.npts = 1
    obs += __create_trace('H', [1])
    obs += __create_trace('E', [1])
    obs += __create_trace('Z', [1])
    obs += __create_trace('F', [1])
    geo = StreamConverter.get_geo_from_obs(obs)
    X = geo.select(channel='X')[0].data
    Y = geo.select(channel='Y')[0].data
    assert_almost_equals(X[0], 1, 9,
        'Expect X to almost equal 1', True)
    assert_almost_equals(Y[0], 1, 9,
        'Expect Y to almost equal 1', True)

    # 2) Call get_geo_from_obs using a decbas of 15 degrees, and streams
    #   with H = [cos(15), cos(30)], and E = [sin(15), sin(30)].
    #   Expect streams of X = [cos(30), cos(45)] and Y = sin(30), sin(45)
    obs = obspy.core.Stream()
    stats.DECBAS = 15 * D2I
    stats.npts = 2
    obs += __create_trace('H', [cos(15 * D2R), cos(30 * D2R)])
    obs += __create_trace('E', [sin(15 * D2R), sin(30 * D2R)])
    obs += __create_trace('Z', [1, 1])
    obs += __create_trace('F', [1, 1])
    geo = StreamConverter.get_geo_from_obs(obs)
    X = geo.select(channel='X')[0].data
    Y = geo.select(channel='Y')[0].data
    assert_equals(X, [cos(30 * D2R), cos(45 * D2R)],
        'Expect X to equal [cos(30), cos(45)]', True)
    assert_equals(Y, [sin(30 * D2R), sin(45 * D2R)],
        'Expect Y to equal [sin(30), sin(45)]', True)


def test_get_mag_from_geo():
    """geomag.StreamConverter_test.test_get_mag_from_geo()

    The geographic stream containing the traces ''x'', ''y'', ''z'', and
        ''f'' converts to the magnetic stream containing the traces
        ''h'', ''d'', ''z'' and ''f''.
    """
    geo = obspy.core.Stream()

    # Call get_mag_from_geo using a decbas of 15, a X stream of
    #   [cos(15), cos(30)], and a Y stream of [sin(15), sin(30)].
    #   Expect a H stream of [1,1] and a D strem of [15 degrees, 30 degrees]
    stats.DECBAS = 15 * D2I
    stats.npts = 2
    geo += __create_trace('X', [cos(15 * D2R), cos(30 * D2R)])
    geo += __create_trace('Y', [sin(15 * D2R), sin(30 * D2R)])
    geo += __create_trace('Z', [1, 1])
    geo += __create_trace('F', [1, 1])
    mag = StreamConverter.get_mag_from_geo(geo)
    H = mag.select(channel='H')[0].data
    D = mag.select(channel='D')[0].data
    assert_equals(H, [1, 1],
        'Expect H to equal [1,1]', True)
    assert_equals(D, [15 * D2R, 30 * D2R],
        'Expect D to equal [15 degrees, 30 degrees]', True)


def test_get_mag_from_obs():
    """geomag.StreamConverter_test.test_get_mag_from_obs()

    The observatory stream containing the traces ''h'', ''e'' or ''d'',
        ''z'' and ''f''
    """
    obs = obspy.core.Stream()

    # Call get_mag_from_obs using a DECBAS of 15 degrees, a H stream of
    #   [cos(15), cos(30)] and a E stream of [sin(15), sin(30)].
    #   Expect a H stream of [1, 1] and a D stream of [30 degrees, 45 degrees]
    stats.DECBAS = 15 * D2I
    stats.npts = 2
    obs += __create_trace('H', [cos(15 * D2R), cos(30 * D2R)])
    obs += __create_trace('E', [sin(15 * D2R), sin(30 * D2R)])
    obs += __create_trace('Z', [1, 1])
    obs += __create_trace('F', [1, 1])
    mag = StreamConverter.get_mag_from_obs(obs)
    H = mag.select(channel='H')[0].data
    D = mag.select(channel='D')[0].data
    assert_equals(H, [1, 1],
        'Expect H to equal [1,1]', True)
    assert_equals(D, [30 * D2R, 45 * D2R],
        'Expect D to equal [30 degrees, 45 degrees]', True)


def test_get_obs_from_geo():
    """geomag.StreamConverter_test.test_get_obs_from_geo()

    The geographic stream containing the traces ''x'', ''y'', ''z'', and
    ''f'' converts to the observatory stream containing the traces
    ''h'', ''d'' or ''e'', ''z'', and ''f''.
    """
    geo = obspy.core.Stream()

    # Call get_geo_from_obs using a decbas of 15, a X stream of
    #   [cos(30), cos(45)], and a Y stream of [sin(30), sin(45)].
    #   Expect a H stream of [cos(15), cos(30)] and a
    #   E stream of [sin(15), sin(30)]
    stats.DECBAS = 15 * D2I
    stats.npts = 2
    geo += __create_trace('X', [cos(30 * D2R), cos(45 * D2R)])
    geo += __create_trace('Y', [sin(30 * D2R), sin(45 * D2R)])
    geo += __create_trace('Z', [1, 1])
    geo += __create_trace('F', [1, 1])
    obs = StreamConverter.get_obs_from_geo(geo, True)
    H = obs.select(channel='H')[0].data
    E = obs.select(channel='E')[0].data
    D = obs.select(channel='D')[0].data
    assert_almost_equals(H, [cos(15 * D2R), cos(30 * D2R)], 9,
        'Expect H to equal [cos(15), cos(30)]', True)
    assert_almost_equals(E, [sin(15 * D2R), sin(30 * D2R)], 9,
        'Expect E to equal [sin(15), sin(30)', True)
    assert_almost_equals(D, [15 * D2R, 30 * D2R], 9,
        'Expect D to equal [15 degress, 30 degrees]', True)


def test_get_obs_from_mag():
    """geomag.StreamConverter_test.test_get_obs_from_mag()

    The magnetic stream containing the traces ''h'', ''d'', ''z'', and ''f''
        converts to the observatory stream containing the traces
        ''h'', ''e'' and/or ''d'', ''z'', and ''f''
    """
    mag = obspy.core.Stream()

    # Call get_obs_from_mag using a decbas of 15, a H stream of [1,1],
    #   and a D stream of [30 degrees, 45 degrees]. Expect a H stream
    #   of [cos(15), cos(30)], a D stream of [30 degrees, 45 degrees],
    #   and a E stream of [sin(15), sin(30)]
    stats.DECBAS = 15 * D2I
    stats.npts = 2
    mag += __create_trace('H', [1, 1])
    mag += __create_trace('D', [30 * D2R, 45 * D2R])
    mag += __create_trace('Z', [1, 1])
    mag += __create_trace('F', [1, 1])
    obs = StreamConverter.get_obs_from_mag(mag, True)
    H = obs.select(channel='H')[0].data
    D = obs.select(channel='D')[0].data
    E = obs.select(channel='E')[0].data
    assert_almost_equals(H, [cos(15 * D2R), cos(30 * D2R)], 9,
        'Expect H to equal [cos(15), cos(30)', True)
    assert_almost_equals(D, [15 * D2R, 30 * D2R], 9,
        'Expect D to equal [15 degrees, 30 degrees', True)
    assert_almost_equals(E, [sin(15 * D2R), sin(30 * D2R)], 9,
        'Expect E to equal [sin(15), sin(30)', True)


def test_get_obs_from_obs():
    """geomag.StreamConverter_test.test_get_obs_from_obs()

    The observatory stream can contain either ''d'' or ''e'' depending
    on it's source. get_obs_from_obs will return either or both as part
    of the obs Stream.
    """

    # 1) Call get_obs_from_obs using a decbas of 15, a H stream of
    #   [cos(15), cos(30)], and a E stream of [sin(15), sin(30)].
    #   Expect a D stream of [15 degrees, 30 degrees]
    obs_e = obspy.core.Stream()
    stats.DECBAS = 15 * D2I
    stats.npts = 2
    obs_e += __create_trace('H', [cos(15 * D2R), cos(30 * D2R)])
    obs_e += __create_trace('E', [sin(15 * D2R), sin(30 * D2R)])
    obs_e += __create_trace('Z', [1, 1])
    obs_e += __create_trace('F', [1, 1])
    obs_D = StreamConverter.get_obs_from_obs(obs_e, False, True)
    d = obs_D.select(channel='D')[0].data
    assert_almost_equals(d, [15 * D2R, 30 * D2R], 9,
        'Expect D to equal [15 degrees, 30 degrees]', True)

    # 2) Call get_obs_from_obs using a decbase of 15 degrees, a H stream of
    #   [cos(15), cos(30)], and a D stream of [15, 30].
    #   Expect a D stream of [sin(15), sin(30)]
    obs_d = obspy.core.Stream()
    obs_d += __create_trace('H', [cos(15 * D2R), cos(30 * D2R)])
    obs_d += __create_trace('D', [15 * D2R, 30 * D2R])
    obs_d += __create_trace('Z', [1, 1])
    obs_d += __create_trace('F', [1, 1])
    obs_E = StreamConverter.get_obs_from_obs(obs_d, True, False)
    e = obs_E.select(channel='E')[0].data
    assert_almost_equals(e, [sin(15 * D2R), sin(30 * D2R)], 9,
        'Expect E to equal [sin(15), sin(30)', True)


def test_verification_data():
    """
    This is a verification test of data done with different
    converters,  to see if the same result is returned.
    Since the small angle approximation was used in the other
    converters, AND round off was done differently,  we can't
    get the exact results.
    Change the precision in assert_almost_equals to larger precision
    (ie 2 to 8) to see how off the data is. Most are well within
    expectations.
    """
    stats.DECBAS = 552.7
    stats.npts = 6
    obs_v = obspy.core.Stream()
    obs_v += __create_trace('H',
        [20889.55, 20889.57, 20889.74, 20889.86, 20889.91, 20889.81])
    obs_v += __create_trace('E',
        [-21.10, -20.89, -20.72, -20.57, -20.39, -20.12])
    obs_v += __create_trace('Z',
        [47565.29, 47565.34, 47565.39, 47565.45, 47565.51, 47565.54])
    obs_v += __create_trace('F',
        [52485.77, 52485.84, 52485.94, 52486.06, 52486.11, 52486.10])
    obs_V = StreamConverter.get_obs_from_obs(obs_v, True, True)
    d = obs_V.select(channel='D')[0].data
    d = ChannelConverter.get_minutes_from_radians(d)
    # Using d values calculated using small angle approximation.
    assert_almost_equals(d,
        [-3.47, -3.43, -3.40, -3.38, -3.35, -3.31], 2,
        'Expect d to equal [-3.47, -3.43, -3.40, -3.38, -3.35, -3.31]', True)

    mag = obspy.core.Stream()
    stats.DECBAS = 552.7
    stats.npts = 6
    mag += __create_trace('H',
        [20884.04, 20883.45, 20883.38, 20883.43, 20883.07, 20882.76])
    d = ChannelConverter.get_radians_from_minutes(
        [556.51, 556.52, 556.56, 556.61, 556.65, 556.64])
    mag += __create_trace('D', d)
    mag += __create_trace('Z',
        [48546.90, 48546.80, 48546.80, 48546.70, 48546.80, 48546.90])
    mag += __create_trace('F',
        [0.10, 0.00, 0.10, 0.00, 0.00, 0.00, 0.00])
    geo = StreamConverter.get_geo_from_mag(mag)
    X = geo.select(channel='X')[0].data
    Y = geo.select(channel='Y')[0].data
    assert_almost_equals(X,
        [20611.00, 20610.40, 20610.30, 20610.30, 20609.90, 20609.60], 2)
    assert_almost_equals(Y,
        [3366.00, 3366.00, 3366.20, 3366.50, 3366.70, 3366.60], 1)


def __create_trace(channel, data):
    """
    Utility to create a trace containing the given numpy array.

    Parameters
    ----------
    channel: string
        The name of the trace being created.
    data: array
        The array to be inserted into the trace.

    Returns
    -------
    obspy.core.Stream
        Stream containing the channel.
    """
    stats.channel = channel
    numpy_data = numpy.array(data, dtype=numpy.float64)
    return obspy.core.Trace(numpy_data, stats)
