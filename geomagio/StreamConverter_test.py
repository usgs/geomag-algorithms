
import obspy.core
import numpy
import StreamConverter

assert_equals = numpy.testing.assert_equal
assert_almost_equals = numpy.testing.assert_almost_equal

cos = numpy.cos
sin = numpy.sin
# tan = math.tan

D2R = numpy.pi / 180
M2I = 60 * 10               # Minutes to Iaga Decbas
STARTTIME = obspy.core.UTCDateTime('2014-11-01')

stats = obspy.core.Stats()
stats.comments = ""
stats.starttime = STARTTIME
stats.sampling_rate = 0.0166666666667
stats.npts = 1
stats.DECBAS = 0

"""Unit Tests for StreamConverter

Notes
-----

We are using triangle identities for variables to test with.  Specifically
    the hypotenuse is normally equal to 1, causing the adjacent angle length
    to be cos(angle) and the opposite length to be sin(angle)

For more info on the components see the Notes in ChannelConverterTest.py.
"""


def test_get_geo_from_obs():
    """geomag.StreamConverter.test_get_geo_from_obs()

    The observatory stream containing the observatory traces
    ''h'', ''d'' or ''e'', ''z'', and ''f'' converts to the geographic
    stream containing the traces ''x'', ''y'', ''z'', and ''f''
    """
    obs = obspy.core.Stream()

    # 1) call get_geo_from_obs using equal h, e streams with a decbas of 0
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
    assert_almost_equals(X[0], 1, 8, 'Expect X to almost equal 1', True)
    assert_almost_equals(Y[0], 1, 8, 'Expect Y to almost equal 1', True)

    # 2) call get_geo_from_obs using a decbas of 15 degrees, and streams
    #   with H = [cos(15), cos(30)], and E = [sin(15), sin(30)].
    #   Expect treams of X = [cos(30), cos(45)] and Y = sin(30), sin(45)
    obs = obspy.core.Stream()
    stats.DECBAS = 15 * M2I
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


def test_get_obs_from_geo():
    """geomag.StreamConverter.test_get_obs_from_geo()

    The geographic stream containing the traces ''x'', ''y'', ''z'', and
    ''f'' converts to the observatory stream containing the traces
    ''h'', ''d'' or ''e'', ''z'', and ''f''.
    """
    geo = obspy.core.Stream()

    # call get_geo_from_obs using a decbas of 15, a X stream of
    #   [cos(30), cos(45)], and a Y stream of [sin(30), sin(45)].
    #   Expect a H stream of [cos(15), cos(30)] and a
    #   E stream of [sin(15), sin(30)]
    stats.DECBAS = 15 * M2I
    stats.npts = 2
    geo += __create_trace('X', [cos(30 * D2R), cos(45 * D2R)])
    geo += __create_trace('Y', [sin(30 * D2R), sin(45 * D2R)])
    geo += __create_trace('Z', [1, 1])
    geo += __create_trace('F', [1, 1])
    obs = StreamConverter.get_obs_from_geo(geo, True)
    H = obs.select(channel='H')[0].data
    E = obs.select(channel='E')[0].data
    D = obs.select(channel='D')[0].data
    assert_almost_equals(H, [cos(15 * D2R), cos(30 * D2R)], 8,
        'Expect H to equal [cos(15), cos(30)]', True)
    assert_almost_equals(E, [sin(15 * D2R), sin(30 * D2R)], 8,
        'Expect E to equal [sin(15), sin(30)', True)
    assert_almost_equals(D, [15 * D2R, 30 * D2R], 8,
        'Expect D to equal [15 degress, 30 degrees]', True)


def test_get_obs_from_obs():
    """geomag.StreamConverter.test_get_obs_from_obs()

    The observatory stream can contain either ''d'' or ''e'' depending
    on it's source. get_obs_from_obs will return either or both as part
    of the obs Stream.
    """

    # 1) Call get_obs_from_obs using a decbas of 15, a H stream of
    #   [cos(15), cos(30)], a E stream of [sin(15), sin(30)].
    #   Expect a D stream of [15 degrees, 30 degrees]
    obs_e = obspy.core.Stream()
    stats.DECBAS = 15 * M2I
    stats.npts = 2
    obs_e += __create_trace('H', [cos(15 * D2R), cos(30 * D2R)])
    obs_e += __create_trace('E', [sin(15 * D2R), sin(30 * D2R)])
    obs_e += __create_trace('Z', [1, 1])
    obs_e += __create_trace('F', [1, 1])
    obs_D = StreamConverter.get_obs_from_obs(obs_e, False, True)
    d = obs_D.select(channel='D')[0].data
    assert_almost_equals(d, [15 * D2R, 30 * D2R], 8)

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
    assert_almost_equals(e, [sin(15 * D2R), sin(30 * D2R)], 8,
        'Expect E to equal [sin(15), sin(30)')


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
