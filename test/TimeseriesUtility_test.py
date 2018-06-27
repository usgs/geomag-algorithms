#! /usr/bin/env python
from __future__ import absolute_import

from nose.tools import assert_equals
from .StreamConverter_test import __create_trace
import numpy
from geomagio import TimeseriesUtility
from obspy.core import Stream, UTCDateTime


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
