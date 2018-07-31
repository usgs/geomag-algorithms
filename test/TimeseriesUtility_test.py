#! /usr/bin/env python
from __future__ import absolute_import

from nose.tools import assert_equals
from .StreamConverter_test import __create_trace
import numpy
from geomagio import TimeseriesUtility
from obspy.core import Stream, UTCDateTime

assert_almost_equal = numpy.testing.assert_almost_equal


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
    assert_equals(len(gaps['H']), 2)
    # gap at start of H
    gap = gaps['H'][0]
    assert_equals(gap[0], UTCDateTime('2015-01-01T00:00:00Z'))
    assert_equals(gap[1], UTCDateTime('2015-01-01T00:00:00Z'))
    # gap at end of H
    gap = gaps['H'][1]
    assert_equals(gap[0], UTCDateTime('2015-01-01T00:00:03Z'))
    assert_equals(gap[1], UTCDateTime('2015-01-01T00:00:04Z'))
    # no gaps in Z channel
    assert_equals(len(gaps['Z']), 0)


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
    assert_equals('H' in gaps, False)
    assert_equals(len(gaps['Z']), 0)


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
    assert_equals(len(gaps), 1)
    gap = gaps[0]
    assert_equals(gap[0], UTCDateTime('2015-01-01T00:02:00Z'))
    assert_equals(gap[1], UTCDateTime('2015-01-01T00:03:00Z'))


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
    assert_equals(len(merged), 2)
    # first gap combines H and Z gaps
    gap = merged[0]
    assert_equals(gap[0], UTCDateTime('2015-01-01T00:00:00Z'))
    assert_equals(gap[1], UTCDateTime('2015-01-01T00:00:03Z'))
    # second gap is second Z gap
    gap = merged[1]
    assert_equals(gap[0], UTCDateTime('2015-01-01T00:00:05Z'))
    assert_equals(gap[1], UTCDateTime('2015-01-01T00:00:07Z'))


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
    assert_equals(1, len(merged_streams1.select(channel='F')))
    # Merge multiple streams with overlapping timestamps
    timeseries = timeseries1 + timeseries2

    merged_streams = TimeseriesUtility.merge_streams(timeseries)
    assert_equals(len(merged_streams), len(timeseries1))
    assert_equals(len(merged_streams[0]), 6)
    assert_equals(len(merged_streams[2]), 6)
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
    assert_equals(len(timeseries3), len(merged_streams3))
    assert_almost_equal(
            timeseries3.select(channel='H')[0].data,
            [1, 1, 1, 1])
    assert_equals(
            numpy.isnan(timeseries3.select(channel='E')[0].data).all(),
            True)
    assert_equals(
            numpy.isnan(timeseries3.select(channel='F')[0].data).all(),
            True)

    trace10 = __create_trace('H', [1, 1, numpy.nan, numpy.nan, 1, 1])
    trace11 = __create_trace('H', [2, 2, 2, 2])
    trace10.stats.starttime = UTCDateTime('2018-01-01T00:00:00Z')
    trace11.stats.starttime = UTCDateTime('2018-01-01T00:01:00Z')
    timeseries4 = Stream(traces=[trace10, trace11])
    merged4 = TimeseriesUtility.merge_streams(timeseries4)
    assert_equals(len(merged4[0].data), 6)
    assert_almost_equal(
        merged4.select(channel='H')[0].data,
        [1, 2, 2, 2, 1, 1])
