"""Tests for EdgeFactory.py"""

from obspy.core import Stats, Stream, Trace, UTCDateTime
from geomagio.edge import EdgeFactory
from nose.tools import assert_equals
import numpy as np


def test__get_edge_network():
    """edge_test.EdgeFactory_test.test__get_edge_network()
    """
    # _get_edge_network should always return NT for use by USGS geomag
    assert_equals(EdgeFactory()._get_edge_network(' ', ' ', ' ', ' '), 'NT')


def test__get_edge_station():
    """edge_test.EdgeFactory_test.test__get_edge_station()
    """
    # _get_edge_station will return the observatory code passed in.
    assert_equals(EdgeFactory()._get_edge_station('BOU', ' ', ' ', ' '), 'BOU')


def test__get_edge_channel():
    """edge_test.EdgeFactory_test.test__get_edge_channel()
    """
    # Call private function _get_edge_channel, make certain
    # it gets back the appropriate 2 character code.
    assert_equals(EdgeFactory()._get_edge_channel('', 'D', '', 'minute'),
            'MVD')
    assert_equals(EdgeFactory()._get_edge_channel('', 'E', '', 'minute'),
            'MVE')
    assert_equals(EdgeFactory()._get_edge_channel('', 'F', '', 'minute'),
            'MSF')
    assert_equals(EdgeFactory()._get_edge_channel('', 'H', '', 'minute'),
            'MVH')
    assert_equals(EdgeFactory()._get_edge_channel('', 'DIST', '', 'minute'),
            'MDT')
    assert_equals(EdgeFactory()._get_edge_channel('', 'DST', '', 'minute'),
            'MGD')
    assert_equals(EdgeFactory()._get_edge_channel('', 'E-E', '', 'minute'),
            'MQE')
    assert_equals(EdgeFactory()._get_edge_channel('', 'E-N', '', 'minute'),
            'MQN')


def test__get_edge_location():
    """edge_test.EdgeFactory_test.test__get_edge_location()
    """
    # Call _get_edge_location, make certain it returns the correct edge
    # location code.
    assert_equals(EdgeFactory()._get_edge_location(
            '', '', 'variation', ''), 'R0')
    assert_equals(EdgeFactory()._get_edge_location(
            '', '', 'quasi-definitive', ''), 'Q0')
    assert_equals(EdgeFactory()._get_edge_location(
            '', '', 'definitive', ''), 'D0')


def test__get_interval_code():
    """edge_test.EdgeFactory_test.test__get_interval_code()
    """
    assert_equals(EdgeFactory()._get_interval_code('daily'), 'D')
    assert_equals(EdgeFactory()._get_interval_code('hourly'), 'H')
    assert_equals(EdgeFactory()._get_interval_code('minute'), 'M')
    assert_equals(EdgeFactory()._get_interval_code('second'), 'S')


def test__set_metadata():
    """edge_test.EdgeFactory_test.test__set_metadata()
    """
    # Call _set_metadata with 2 traces,  and make certain the stats get
    # set for both traces.
    trace1 = Trace()
    trace2 = Trace()
    stream = Stream(traces=[trace1, trace2])
    EdgeFactory()._set_metadata(stream, 'BOU', 'H', 'variation', 'minute')
    assert_equals(stream[0].stats['channel'], 'H')
    assert_equals(stream[1].stats['channel'], 'H')


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
    assert_equals(timeseries.select(channel='H')[0].stats.station,
        'BOU', 'Expect timeseries to have stats')
    assert_equals(timeseries.select(channel='H')[0].stats.channel,
        'H', 'Expect timeseries stats channel to be equal to H')


def test_clean_timeseries():
    """edge_test.EdgeFactory_test.test_clean_timeseries()
    """
    edge_factory = EdgeFactory()
    trace1 = _create_trace([1, 1, 1, 1, 1], 'H', UTCDateTime("2018-01-01"))
    trace2 = _create_trace([2, 2], 'E', UTCDateTime("2018-01-01"))
    timeseries = Stream(traces=[trace1, trace2])
    edge_factory._clean_timeseries(
        timeseries=timeseries,
        starttime=trace1.stats.starttime,
        endtime=trace1.stats.endtime)
    assert_equals(len(trace1.data), len(trace2.data))
    assert_equals(trace1.stats.starttime, trace2.stats.starttime)
    assert_equals(trace1.stats.endtime, trace2.stats.endtime)
    # change starttime by less than 1 delta
    starttime = trace1.stats.starttime
    endtime = trace1.stats.endtime
    edge_factory._clean_timeseries(timeseries, starttime - 30, endtime + 30)
    assert_equals(trace1.stats.starttime, starttime)
    # Change starttime by more than 1 delta
    edge_factory._clean_timeseries(timeseries, starttime - 90, endtime + 90)
    assert_equals(trace1.stats.starttime, starttime - 60)
    assert_equals(np.isnan(trace1.data[0]), np.isnan(np.NaN))


def test_create_missing_channel():
    """edge_test.EdgeFactory_test.test_create_missing_channel()
    """
    edge_factory = EdgeFactory()
    trace1 = _create_trace([1, 1, 1, 1, 1], 'H', UTCDateTime("2018-01-01"))
    trace2 = _create_trace([2, 2], 'E', UTCDateTime("2018-01-01"))
    observatory = 'Test'
    type = 'variation'
    interval = 'minute'
    network = 'NT'
    location = 'R0'
    trace3 = edge_factory._create_missing_channel(
        starttime=trace1.stats.starttime,
        endtime=trace1.stats.endtime,
        observatory=observatory,
        channel='F',
        type=type,
        interval=interval,
        network=network,
        station=trace1.stats.station,
        location=location)
    timeseries = Stream(traces=[trace1, trace2])
    # For continuity set stats to be same for all traces
    for trace in timeseries:
        trace.stats.observatory = observatory
        trace.stats.type = type
        trace.stats.interval = interval
        trace.stats.network = network
        trace.stats.station = trace1.stats.station
        trace.stats.location = location
    timeseries += trace3
    assert_equals(len(trace3[0].data), trace3[0].stats.npts)
    assert_equals(timeseries[0].stats.starttime, timeseries[2].stats.starttime)
    edge_factory._clean_timeseries(
        timeseries=timeseries,
        starttime=trace1.stats.starttime,
        endtime=trace1.stats.endtime)
    assert_equals(len(trace3[0].data), trace3[0].stats.npts)
    assert_equals(timeseries[0].stats.starttime, timeseries[2].stats.starttime)
    # Change starttime by more than 1 delta
    starttime = trace1.stats.starttime
    endtime = trace1.stats.endtime
    edge_factory._clean_timeseries(timeseries, starttime - 90, endtime + 90)
    assert_equals(len(trace3[0].data), trace3[0].stats.npts)
    assert_equals(timeseries[0].stats.starttime, timeseries[2].stats.starttime)


def _create_trace(data, channel, starttime, delta=60.):
    stats = Stats()
    stats.channel = channel
    stats.delta = delta
    stats.starttime = starttime
    stats.npts = len(data)
    data = np.array(data, dtype=np.float64)
    return Trace(data, stats)
