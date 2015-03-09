"""Tests for EdgeFactory.py"""

from obspy.core.utcdatetime import UTCDateTime
from EdgeFactory import EdgeFactory
from nose.tools import assert_equals
from nose.tools import assert_raises
from geomagio import TimeseriesFactoryException


def test_get_edge_channel_codes():
    """geomagio.edge.EdgeFactory_test.test_get_edge_channel_codes()
    """
    # 1) Call get_edge_channel_codes with minute, variation and H,
    #    expect MVH back
    channels = EdgeFactory().get_edge_channel_codes('BOU', ('H'), 'variation',
        'minute')
    assert_equals(channels, ['MVH'], 'Expect edge channel to equal MVH')
    # 2) Call get_edge_channel_codes with second, variation and [H,D,Z,F],
    #    expect SVN, SVD, SVZ and SSF back
    channels = EdgeFactory().get_edge_channel_codes('BOU',
        ('H', 'D', 'Z', 'F'), 'variation', 'second')
    assert_equals(channels[0], 'SVH', 'Expect edge channels to equal SVH')
    assert_equals(channels[1], 'SVD', 'Expect edge channels to equal SVD')
    assert_equals(channels[2], 'SVZ', 'Expect edge channels to equal SVZ')
    assert_equals(channels[3], 'SSF', 'Expect edge channels to equal SSF')


def test_get_interval_from_edge():
    """geomagio.edge.EdgeFactory_test.test_get_interval_from_edge()
    """
    # 1) Call get_interval_from_edge with Minute channels, get minute back.
    assert_equals(EdgeFactory().get_interval_from_edge(
        ('MVH', 'MVE')), 'minute')
    # 2) Call get_interval_from_edge with Mixed channels, raise exception.
    assert_raises(TimeseriesFactoryException,
        EdgeFactory().get_interval_from_edge,
        ('MVH', 'SVE'))


def test__get_edge_code_from_channel():
    """geomagio.edge.EdgeFactory_test.test__get_edge_code_from_channel()
    """
    # Call private function _get_edge_code_from_channel, make certain
    # it gets back the appropriate 2 character code.
    assert_equals(EdgeFactory()._get_edge_code_from_channel('D'), 'VD')
    assert_equals(EdgeFactory()._get_edge_code_from_channel('E'), 'VE')
    assert_equals(EdgeFactory()._get_edge_code_from_channel('F'), 'SF')
    assert_equals(EdgeFactory()._get_edge_code_from_channel('H'), 'VH')
    assert_equals(EdgeFactory()._get_edge_code_from_channel('Z'), 'VZ')


# def test_get_timeseries():
def dont_get_timeseries():
    """geomagio.edge.EdgeFactory_test.test_get_timeseries()"""
    # Call get_timeseries, and test stats for comfirmation that it came back.
    # TODO, need to pass in host and port from a config file, or manually
    #   change for a single test.
    edge_factory = EdgeFactory(host='TODO', port='TODO')
    timeseries = edge_factory.get_timeseries(
        UTCDateTime(2015, 3, 1, 0, 0, 0), UTCDateTime(2015, 3, 1, 1, 0, 0),
        'BOU', ('H'), 'variation', 'minute')
    assert_equals(timeseries.select(channel='MVH')[0].stats.station,
        'BOU', 'Expect timeseries to have stats')
