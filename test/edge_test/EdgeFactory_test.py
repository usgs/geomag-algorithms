"""Tests for EdgeFactory.py"""

from obspy.core import Stream, Trace, UTCDateTime
from geomagio.edge import EdgeFactory
from numpy.testing import assert_equal


def test__get_edge_network():
    """edge_test.EdgeFactory_test.test__get_edge_network()
    """
    # _get_edge_network should always return NT for use by USGS geomag
    assert_equal(EdgeFactory()._get_edge_network(' ', ' ', ' ', ' '), 'NT')


def test__get_edge_station():
    """edge_test.EdgeFactory_test.test__get_edge_station()
    """
    # _get_edge_station will return the observatory code passed in.
    assert_equal(EdgeFactory()._get_edge_station('BOU', ' ', ' ', ' '), 'BOU')


def test__get_edge_channel():
    """edge_test.EdgeFactory_test.test__get_edge_channel()
    """
    # Call private function _get_edge_channel, make certain
    # it gets back the appropriate 2 character code.
    assert_equal(EdgeFactory()._get_edge_channel('', 'D', '', 'minute'),
            'MVD')
    assert_equal(EdgeFactory()._get_edge_channel('', 'E', '', 'minute'),
            'MVE')
    assert_equal(EdgeFactory()._get_edge_channel('', 'F', '', 'minute'),
            'MSF')
    assert_equal(EdgeFactory()._get_edge_channel('', 'H', '', 'minute'),
            'MVH')
    assert_equal(EdgeFactory()._get_edge_channel('', 'DIST', '', 'minute'),
            'MDT')
    assert_equal(EdgeFactory()._get_edge_channel('', 'DST', '', 'minute'),
            'MGD')
    assert_equal(EdgeFactory()._get_edge_channel('', 'E-E', '', 'minute'),
            'MQE')
    assert_equal(EdgeFactory()._get_edge_channel('', 'E-N', '', 'minute'),
            'MQN')


def test__get_edge_location():
    """edge_test.EdgeFactory_test.test__get_edge_location()
    """
    # Call _get_edge_location, make certain it returns the correct edge
    # location code.
    assert_equal(EdgeFactory()._get_edge_location(
            '', '', 'variation', ''), 'R0')
    assert_equal(EdgeFactory()._get_edge_location(
            '', '', 'quasi-definitive', ''), 'Q0')
    assert_equal(EdgeFactory()._get_edge_location(
            '', '', 'definitive', ''), 'D0')


def test__get_interval_code():
    """edge_test.EdgeFactory_test.test__get_interval_code()
    """
    assert_equal(EdgeFactory()._get_interval_code('day'), 'D')
    assert_equal(EdgeFactory()._get_interval_code('hour'), 'H')
    assert_equal(EdgeFactory()._get_interval_code('minute'), 'M')
    assert_equal(EdgeFactory()._get_interval_code('second'), 'S')


def test__set_metadata():
    """edge_test.EdgeFactory_test.test__set_metadata()
    """
    # Call _set_metadata with 2 traces,  and make certain the stats get
    # set for both traces.
    trace1 = Trace()
    trace2 = Trace()
    stream = Stream(traces=[trace1, trace2])
    EdgeFactory()._set_metadata(stream, 'BOU', 'H', 'variation', 'minute')
    assert_equal(stream[0].stats['channel'], 'H')
    assert_equal(stream[1].stats['channel'], 'H')


# def test_get_timeseries():
def dont_get_timeseries():
    """edge_test.EdgeFactory_test.test_get_timeseries()"""
    # Call get_timeseries, and test stats for comfirmation that it came back.
    # TODO, need to pass in host and port from a config file, or manually
    #   change for a single test.
    edge_factory = EdgeFactory(host='TODO', port='TODO')
    timeseries = edge_factory.get_timeseries(
        UTCDateTime(2015, 3, 1, 0, 0, 0), UTCDateTime(2015, 3, 1, 1, 0, 0),
        'BOU', ('H'), 'variation', 'minute')
    assert_equal(timeseries.select(channel='H')[0].stats.station,
        'BOU', 'Expect timeseries to have stats')
    assert_equal(timeseries.select(channel='H')[0].stats.channel,
        'H', 'Expect timeseries stats channel to be equal to H')
