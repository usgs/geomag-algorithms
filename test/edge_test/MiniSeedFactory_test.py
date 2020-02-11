"""Tests for MiniSeedFactory.py"""

import numpy
from numpy.testing import assert_equal
from obspy.core import Stats, Stream, Trace, UTCDateTime
from geomagio import TimeseriesUtility
from geomagio.edge import MiniSeedFactory


def test__get_edge_network():
    """edge_test.MiniSeedFactory_test.test__get_edge_network()
    """
    # _get_edge_network should always return NT for use by USGS geomag
    assert_equal(
            MiniSeedFactory()._get_edge_network(' ', ' ', ' ', ' '),
            'NT')


def test__get_edge_station():
    """edge_test.MiniSeedFactory_test.test__get_edge_station()
    """
    # _get_edge_station will return the observatory code passed in.
    assert_equal(
            MiniSeedFactory()._get_edge_station('BOU', ' ', ' ', ' '),
            'BOU')


def test__get_edge_channel():
    """edge_test.MiniSeedFactory_test.test__get_edge_channel()
    """
    # Call private function _get_edge_channel, make certain
    # it gets back the appropriate 2 character code.
    factory = MiniSeedFactory()
    assert_equal(factory._get_edge_channel('', 'D', '', 'minute'), 'UFD')
    assert_equal(factory._get_edge_channel('', 'U', '', 'minute'), 'UFU')
    assert_equal(factory._get_edge_channel('', 'F', '', 'minute'), 'UFF')
    assert_equal(factory._get_edge_channel('', 'H', '', 'minute'), 'UFH')
    assert_equal(factory._get_edge_channel('', 'BEU', '', 'minute'), 'BEU')
    assert_equal(factory._get_edge_channel('', 'Dst4', '', 'minute'), 'UX4')
    assert_equal(factory._get_edge_channel('', 'Dst3', '', 'minute'), 'UX3')
    assert_equal(factory._get_edge_channel('', 'E-E', '', 'minute'), 'UQE')
    assert_equal(factory._get_edge_channel('', 'E-N', '', 'minute'), 'UQN')


def test__get_edge_location():
    """edge_test.MiniSeedFactory_test.test__get_edge_location()
    """
    # Call _get_edge_location, make certain it returns the correct edge
    # location code.
    assert_equal(MiniSeedFactory()._get_edge_location(
            '', '', 'variation', ''), 'R0')
    assert_equal(MiniSeedFactory()._get_edge_location(
            '', '', 'quasi-definitive', ''), 'Q0')
    assert_equal(MiniSeedFactory()._get_edge_location(
            '', '', 'definitive', ''), 'D0')


def test__get_interval_code():
    """edge_test.MiniSeedFactory_test.test__get_interval_code()
    """
    assert_equal(MiniSeedFactory()._get_interval_code('day'), 'P')
    assert_equal(MiniSeedFactory()._get_interval_code('hour'), 'R')
    assert_equal(MiniSeedFactory()._get_interval_code('minute'), 'U')
    assert_equal(MiniSeedFactory()._get_interval_code('second'), 'L')
    assert_equal(MiniSeedFactory()._get_interval_code('tenhertz'), 'B')


class MockMiniSeedInputClient(object):
    def __init__(self):
        self.close_called = False
        self.last_sent = None

    def close(self):
        self.close_called = True

    def send(self, stream):
        self.last_sent = stream


def test__put_timeseries():
    """edge_test.MiniSeedFactory_test.test__put_timeseries()
    """
    trace1 = __create_trace([0, 1, 2, 3, numpy.nan, 5, 6, 7, 8, 9],
            channel='H')
    client = MockMiniSeedInputClient()
    factory = MiniSeedFactory()
    factory.write_client = client
    factory.put_timeseries(Stream(trace1), channels=('H'))
    # put timeseries should call close when done
    assert_equal(client.close_called, True)
    # trace should be split in 2 blocks at gap
    sent = client.last_sent
    assert_equal(len(sent), 2)
    # first trace includes [0...4]
    assert_equal(sent[0].stats.channel, 'LFH')
    assert_equal(len(sent[0]), 4)
    assert_equal(sent[0].stats.endtime, trace1.stats.starttime + 3)
    # second trace includes [5...9]
    assert_equal(sent[1].stats.channel, 'LFH')
    assert_equal(len(sent[1]), 5)
    assert_equal(sent[1].stats.starttime, trace1.stats.starttime + 5)
    assert_equal(sent[1].stats.endtime, trace1.stats.endtime)


def test__set_metadata():
    """edge_test.MiniSeedFactory_test.test__set_metadata()
    """
    # Call _set_metadata with 2 traces,  and make certain the stats get
    # set for both traces.
    trace1 = Trace()
    trace2 = Trace()
    stream = Stream(traces=[trace1, trace2])
    MiniSeedFactory()._set_metadata(stream, 'BOU', 'H', 'variation', 'minute')
    assert_equal(stream[0].stats['channel'], 'H')
    assert_equal(stream[1].stats['channel'], 'H')


# def test_get_timeseries():
def dont_get_timeseries():
    """edge_test.MiniSeedFactory_test.test_get_timeseries()"""
    # Call get_timeseries, and test stats for comfirmation that it came back.
    # TODO, need to pass in host and port from a config file, or manually
    #   change for a single test.
    edge_factory = MiniSeedFactory(host='TODO', port='TODO')
    timeseries = edge_factory.get_timeseries(
        UTCDateTime(2015, 3, 1, 0, 0, 0), UTCDateTime(2015, 3, 1, 1, 0, 0),
        'BOU', ('H'), 'variation', 'minute')
    assert_equal(timeseries.select(channel='H')[0].stats.station,
        'BOU', 'Expect timeseries to have stats')
    assert_equal(timeseries.select(channel='H')[0].stats.channel,
        'H', 'Expect timeseries stats channel to be equal to H')


def __create_trace(data,
        network='NT',
        station='BOU',
        channel='H',
        location='R0',
        data_interval='second',
        data_type='interval'):
    """
    Utility to create a trace containing the given numpy array.

    Parameters
    ----------
    data: array
        The array to be inserted into the trace.

    Returns
    -------
    obspy.core.Stream
        Stream containing the channel.
    """
    stats = Stats()
    stats.starttime = UTCDateTime('2019-12-01')
    stats.delta = TimeseriesUtility.get_delta_from_interval(data_interval)
    stats.channel = channel
    stats.npts = len(data)
    stats.data_interval = data_interval
    stats.data_type = data_type
    numpy_data = numpy.array(data, dtype=numpy.float64)
    return Trace(numpy_data, stats)
