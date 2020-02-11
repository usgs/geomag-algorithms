#! /usr/bin/env python
from __future__ import absolute_import

from numpy.testing import assert_equal
from .StreamConverter_test import __create_trace
import numpy
from geomagio import TimeseriesUtility
from obspy.core import Stream, Stats, Trace, UTCDateTime

assert_almost_equal = numpy.testing.assert_almost_equal
assert_array_equal = numpy.testing.assert_array_equal


def test_create_empty_trace():
    """TimeseriesUtility_test.test_create_empty_trace()
    """
    trace1 = _create_trace([1, 1, 1, 1, 1], 'H', UTCDateTime("2018-01-01"))
    trace2 = _create_trace([2, 2], 'E', UTCDateTime("2018-01-01"))
    observatory = 'Test'
    interval = 'minute'
    network = 'NT'
    location = 'R0'
    trace3 = TimeseriesUtility.create_empty_trace(
            starttime=trace1.stats.starttime,
            endtime=trace1.stats.endtime,
            observatory=observatory,
            channel='F',
            type='variation',
            interval=interval,
            network=network,
            station=trace1.stats.station,
            location=location)
    timeseries = Stream(traces=[trace1, trace2])
    # For continuity set stats to be same for all traces
    for trace in timeseries:
        trace.stats.observatory = observatory
        trace.stats.type = 'variation'
        trace.stats.interval = interval
        trace.stats.network = network
        trace.stats.station = trace1.stats.station
        trace.stats.location = location
    timeseries += trace3
    assert_equal(len(trace3.data), trace3.stats.npts)
    assert_equal(timeseries[0].stats.starttime, timeseries[2].stats.starttime)
    TimeseriesUtility.pad_timeseries(
        timeseries=timeseries,
        starttime=trace1.stats.starttime,
        endtime=trace1.stats.endtime)
    assert_equal(len(trace3.data), trace3.stats.npts)
    assert_equal(timeseries[0].stats.starttime, timeseries[2].stats.starttime)
    # Change starttime by more than 1 delta
    starttime = trace1.stats.starttime
    endtime = trace1.stats.endtime
    TimeseriesUtility.pad_timeseries(timeseries, starttime - 90, endtime + 90)
    assert_equal(len(trace3.data), trace3.stats.npts)
    assert_equal(timeseries[0].stats.starttime, timeseries[2].stats.starttime)


def test_get_stream_gaps():
    """TimeseriesUtility_test.test_get_stream_gaps()

    confirms that gaps are found in a stream
    """
    stream = Stream([
        __create_trace('H', [numpy.nan, 1, 1, numpy.nan, numpy.nan]),
        __create_trace('Z', [0, 0, 0, 1, 1, 1])
    ])
    for trace in stream:
        # set time of first sample
        trace.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
        # set sample rate to 1 second
        trace.stats.delta = 1
    # find gaps
    gaps = TimeseriesUtility.get_stream_gaps(stream)
    assert_equal(len(gaps['H']), 2)
    # gap at start of H
    gap = gaps['H'][0]
    assert_equal(gap[0], UTCDateTime('2015-01-01T00:00:00Z'))
    assert_equal(gap[1], UTCDateTime('2015-01-01T00:00:00Z'))
    # gap at end of H
    gap = gaps['H'][1]
    assert_equal(gap[0], UTCDateTime('2015-01-01T00:00:03Z'))
    assert_equal(gap[1], UTCDateTime('2015-01-01T00:00:04Z'))
    # no gaps in Z channel
    assert_equal(len(gaps['Z']), 0)


def test_get_stream_gaps_channels():
    """TimeseriesUtility_test.test_get_stream_gaps_channels()

    test that gaps are only checked in specified channels.
    """
    stream = Stream
    stream = Stream([
        __create_trace('H', [numpy.nan, 1, 1, numpy.nan, numpy.nan]),
        __create_trace('Z', [0, 0, 0, 1, 1, 1])
    ])
    for trace in stream:
        # set time of first sample
        trace.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
        # set sample rate to 1 second
        trace.stats.delta = 1
    # find gaps
    gaps = TimeseriesUtility.get_stream_gaps(stream, ['Z'])
    assert_equal('H' in gaps, False)
    assert_equal(len(gaps['Z']), 0)


def test_get_trace_gaps():
    """TimeseriesUtility_test.test_get_trace_gaps()

    confirm that gaps are found in a trace
    """
    trace = __create_trace('H', [1, 1, numpy.nan, numpy.nan, 0, 1])
    # set time of first sample
    trace.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    # set sample rate to 1 minute
    trace.stats.delta = 60
    # find gap
    gaps = TimeseriesUtility.get_trace_gaps(trace)
    assert_equal(len(gaps), 1)
    gap = gaps[0]
    assert_equal(gap[0], UTCDateTime('2015-01-01T00:02:00Z'))
    assert_equal(gap[1], UTCDateTime('2015-01-01T00:03:00Z'))


def test_get_merged_gaps():
    """TimeseriesUtility_test.test_get_merged_gaps()

    confirm that gaps are merged
    """
    merged = TimeseriesUtility.get_merged_gaps({
        'H': [
            # gap for 2 seconds, that starts after next gap
            [
                UTCDateTime('2015-01-01T00:00:01Z'),
                UTCDateTime('2015-01-01T00:00:03Z'),
                UTCDateTime('2015-01-01T00:00:04Z')
            ]
        ],
        # gap for 1 second, that occurs before previous gap
        'Z': [
            [
                UTCDateTime('2015-01-01T00:00:00Z'),
                UTCDateTime('2015-01-01T00:00:00Z'),
                UTCDateTime('2015-01-01T00:00:01Z')
            ],
            [
                UTCDateTime('2015-01-01T00:00:05Z'),
                UTCDateTime('2015-01-01T00:00:07Z'),
                UTCDateTime('2015-01-01T00:00:08Z')
            ],
        ]
    })
    assert_equal(len(merged), 2)
    # first gap combines H and Z gaps
    gap = merged[0]
    assert_equal(gap[0], UTCDateTime('2015-01-01T00:00:00Z'))
    assert_equal(gap[1], UTCDateTime('2015-01-01T00:00:03Z'))
    # second gap is second Z gap
    gap = merged[1]
    assert_equal(gap[0], UTCDateTime('2015-01-01T00:00:05Z'))
    assert_equal(gap[1], UTCDateTime('2015-01-01T00:00:07Z'))


def test_merge_streams():
    """TimeseriesUtility_test.test_merge_streams()

    confirm merge streams treats empty channels correctly
    """
    trace1 = __create_trace('H', [1, 1, 1, 1])
    trace2 = __create_trace('E', [2, numpy.nan, numpy.nan, 2])
    trace3 = __create_trace('F', [numpy.nan, numpy.nan, numpy.nan, numpy.nan])
    trace4 = __create_trace('H', [2, 2, 2, 2])
    trace5 = __create_trace('E', [3, numpy.nan, numpy.nan, 3])
    trace6 = __create_trace('F', [numpy.nan, numpy.nan, numpy.nan, numpy.nan])
    npts1 = len(trace1.data)
    npts2 = len(trace4.data)
    timeseries1 = Stream(traces=[trace1, trace2, trace3])
    timeseries2 = Stream(traces=[trace4, trace5, trace6])
    for trace in timeseries1:
        trace.stats.starttime = UTCDateTime('2018-01-01T00:00:00Z')
        trace.stats.npts = npts1
    for trace in timeseries2:
        trace.stats.starttime = UTCDateTime('2018-01-01T00:02:00Z')
        trace.stats.npts = npts2
    merged_streams1 = TimeseriesUtility.merge_streams(timeseries1)
    # Make sure the empty 'F' was not removed from stream
    assert_equal(1, len(merged_streams1.select(channel='F')))
    # Merge multiple streams with overlapping timestamps
    timeseries = timeseries1 + timeseries2

    merged_streams = TimeseriesUtility.merge_streams(timeseries)
    assert_equal(len(merged_streams), len(timeseries1))
    assert_equal(len(merged_streams[0]), 6)
    assert_equal(len(merged_streams[2]), 6)
    assert_almost_equal(
            merged_streams.select(channel='H')[0].data,
            [1, 1, 2, 2, 2, 2])
    assert_almost_equal(
            merged_streams.select(channel='E')[0].data,
            [2, numpy.nan, 3, 2, numpy.nan, 3])
    assert_almost_equal(
            merged_streams.select(channel='F')[0].data,
            [numpy.nan] * 6)

    trace7 = __create_trace('H', [1, 1, 1, 1])
    trace8 = __create_trace('E', [numpy.nan, numpy.nan, numpy.nan, numpy.nan])
    trace9 = __create_trace('F', [numpy.nan, numpy.nan, numpy.nan, numpy.nan])
    timeseries3 = Stream(traces=[trace7, trace8, trace9])
    npts3 = len(trace7.data)
    for trace in timeseries3:
        trace.stats.starttime = UTCDateTime('2018-01-01T00:00:00Z')
        trace.stats.npts = npts3
    merged_streams3 = TimeseriesUtility.merge_streams(timeseries3)
    assert_equal(len(timeseries3), len(merged_streams3))
    assert_almost_equal(
            timeseries3.select(channel='H')[0].data,
            [1, 1, 1, 1])
    assert_equal(
            numpy.isnan(timeseries3.select(channel='E')[0].data).all(),
            True)
    assert_equal(
            numpy.isnan(timeseries3.select(channel='F')[0].data).all(),
            True)

    trace10 = __create_trace('H', [1, 1, numpy.nan, numpy.nan, 1, 1])
    trace11 = __create_trace('H', [2, 2, 2, 2])
    trace10.stats.starttime = UTCDateTime('2018-01-01T00:00:00Z')
    trace11.stats.starttime = UTCDateTime('2018-01-01T00:01:00Z')
    timeseries4 = Stream(traces=[trace10, trace11])
    merged4 = TimeseriesUtility.merge_streams(timeseries4)
    assert_equal(len(merged4[0].data), 6)
    assert_almost_equal(
        merged4.select(channel='H')[0].data,
        [1, 2, 2, 2, 1, 1])


def test_pad_timeseries():
    """TimeseriesUtility_test.test_pad_timeseries()
    """
    trace1 = _create_trace([1, 1, 1, 1, 1], 'H', UTCDateTime("2018-01-01"))
    trace2 = _create_trace([2, 2], 'E', UTCDateTime("2018-01-01"))
    timeseries = Stream(traces=[trace1, trace2])
    TimeseriesUtility.pad_timeseries(
        timeseries=timeseries,
        starttime=trace1.stats.starttime,
        endtime=trace1.stats.endtime)
    assert_equal(len(trace1.data), len(trace2.data))
    assert_equal(trace1.stats.starttime, trace2.stats.starttime)
    assert_equal(trace1.stats.endtime, trace2.stats.endtime)
    # change starttime by less than 1 delta
    starttime = trace1.stats.starttime
    endtime = trace1.stats.endtime
    TimeseriesUtility.pad_timeseries(timeseries, starttime - 30, endtime + 30)
    assert_equal(trace1.stats.starttime, starttime)
    # Change starttime by more than 1 delta
    TimeseriesUtility.pad_timeseries(timeseries, starttime - 90, endtime + 90)
    assert_equal(trace1.stats.starttime, starttime - 60)
    assert_equal(numpy.isnan(trace1.data[0]), numpy.isnan(numpy.NaN))


def test_pad_and_trim_trace():
    """TimeseriesUtility_test.test_pad_and_trim_trace()
    """
    trace = _create_trace([0, 1, 2, 3, 4], 'X', UTCDateTime("2018-01-01"))
    assert_equal(trace.stats.starttime, UTCDateTime("2018-01-01T00:00:00Z"))
    assert_equal(trace.stats.endtime, UTCDateTime("2018-01-01T00:04:00Z"))
    # starttime between first and second sample
    # expect first sample to be removed, start at next sample, end at same
    TimeseriesUtility.pad_and_trim_trace(trace,
            starttime=UTCDateTime("2018-01-01T00:00:30Z"),
            endtime=trace.stats.endtime)
    assert_equal(trace.stats.starttime, UTCDateTime("2018-01-01T00:01:00Z"))
    assert_equal(trace.stats.endtime, UTCDateTime("2018-01-01T00:04:00Z"))
    assert_array_equal(trace.data, [1, 2, 3, 4])
    # endtime between last and second to last samples
    TimeseriesUtility.pad_and_trim_trace(trace,
            starttime=UTCDateTime("2018-01-01T00:00:30Z"),
            endtime=UTCDateTime("2018-01-01T00:03:50Z"))
    assert_equal(trace.stats.starttime, UTCDateTime("2018-01-01T00:01:00Z"))
    assert_equal(trace.stats.endtime, UTCDateTime("2018-01-01T00:03:00Z"))
    assert_array_equal(trace.data, [1, 2, 3])
    # pad outward
    TimeseriesUtility.pad_and_trim_trace(trace,
            starttime=UTCDateTime("2018-01-01T00:00:00Z"),
            endtime=UTCDateTime("2018-01-01T00:05:00Z"))
    assert_equal(trace.stats.starttime, UTCDateTime("2018-01-01T00:00:00Z"))
    assert_equal(trace.stats.endtime, UTCDateTime("2018-01-01T00:05:00Z"))
    assert_array_equal(trace.data, [numpy.nan, 1, 2, 3, numpy.nan, numpy.nan])
    # remove exactly one sample
    TimeseriesUtility.pad_and_trim_trace(trace,
            starttime=UTCDateTime("2018-01-01T00:00:00Z"),
            endtime=UTCDateTime("2018-01-01T00:04:00Z"))
    assert_equal(trace.stats.starttime, UTCDateTime("2018-01-01T00:00:00Z"))
    assert_equal(trace.stats.endtime, UTCDateTime("2018-01-01T00:04:00Z"))
    assert_array_equal(trace.data, [numpy.nan, 1, 2, 3, numpy.nan])
    # pad start and trim end
    TimeseriesUtility.pad_and_trim_trace(trace,
            starttime=UTCDateTime("2017-12-31T23:58:59Z"),
            endtime=UTCDateTime("2018-01-01T00:03:00Z"))
    assert_equal(trace.stats.starttime, UTCDateTime("2017-12-31T23:59:00Z"))
    assert_equal(trace.stats.endtime, UTCDateTime("2018-01-01T00:03:00Z"))
    assert_array_equal(trace.data, [numpy.nan, numpy.nan, 1, 2, 3])
    # pad end and trim start
    TimeseriesUtility.pad_and_trim_trace(trace,
            starttime=UTCDateTime("2018-01-01T00:00:00Z"),
            endtime=UTCDateTime("2018-01-01T00:04:00Z"))
    assert_equal(trace.stats.starttime, UTCDateTime("2018-01-01T00:00:00Z"))
    assert_equal(trace.stats.endtime, UTCDateTime("2018-01-01T00:04:00Z"))
    assert_array_equal(trace.data, [numpy.nan, 1, 2, 3, numpy.nan])


def _create_trace(data, channel, starttime, delta=60.):
    stats = Stats()
    stats.channel = channel
    stats.delta = delta
    stats.starttime = starttime
    stats.npts = len(data)
    data = numpy.array(data, dtype=numpy.float64)
    return Trace(data, stats)
