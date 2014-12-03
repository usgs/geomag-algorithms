"""Test the Timeseries class."""

from obspy.core.utcdatetime import UTCDateTime
from nose.tools import assert_equals
from Timeseries import Timeseries


def test_get_time():
    """geomag.io.Timeseries_test.test_get_time()

    Construct a timeseries object with 4 samples per channel,
    and known starttime and endtime.
    Verify get_time handles
        - negative indices
        - zero (starttime)
        - length (endtime)
        - beyond length
    """
    timeseries = Timeseries('OBS',
            {
                'H': [1, 2, 3, 4],
                'E': [2, 3, 4, 5],
                'Z': [3, 4, 5, 6],
                'F': [4, 5, 6, 7]
            },
            UTCDateTime('2014-01-01T01:01:01'),
            UTCDateTime('2014-01-01T01:01:04'))
    assert_equals(UTCDateTime('2014-01-01T01:00:59'),
            timeseries.get_time(-2))    
    assert_equals(UTCDateTime('2014-01-01T01:01:01'),
            timeseries.get_time(0))
    assert_equals(UTCDateTime('2014-01-01T01:01:05'),
            timeseries.get_time(len(timeseries)))
    assert_equals(UTCDateTime('2014-01-01T01:01:07'),
            timeseries.get_time(6))

def test_get_index():
    """geomag.io.Timeseries_test.test_get_index()

    Construct a timeseries object with 4 samples per channel,
    and known starttime and endtime.
    Verify get_index handles
        - times before starttime
        - starttime
        - endtime
        - times after endtime
    """
    timeseries = Timeseries('OBS',
            {
                'H': [1, 2, 3, 4],
                'E': [2, 3, 4, 5],
                'Z': [3, 4, 5, 6],
                'F': [4, 5, 6, 7]
            },
            UTCDateTime('2014-01-01T01:01:01'),
            UTCDateTime('2014-01-01T01:01:04'))
    assert_equals(-2,
            timeseries.get_index(UTCDateTime('2014-01-01T01:00:59'), False))   
    assert_equals(0,
            timeseries.get_index(UTCDateTime('2014-01-01T01:01:01'), False))
    assert_equals(len(timeseries),
            timeseries.get_index(UTCDateTime('2014-01-01T01:01:05'), False))
    assert_equals(6,
            timeseries.get_index(UTCDateTime('2014-01-01T01:01:07'), False))

def test_get_index_exact():
    """geomag.io.Timeseries_test.test_get_time()

    Construct a timeseries object with 4 samples per channel,
    and known starttime and endtime.
    Verify get_time returns
        - None when time is between samples
        - index when time is at sample
    """
    timeseries = Timeseries('OBS',
            {
                'H': [1, 2, 3, 4],
                'E': [2, 3, 4, 5],
                'Z': [3, 4, 5, 6],
                'F': [4, 5, 6, 7]
            },
            UTCDateTime('2014-01-01T01:01:01'),
            UTCDateTime('2014-01-01T01:01:04'))
    assert_equals(None,
            timeseries.get_index(UTCDateTime('2014-01-01T01:00:59.5'), True))
    assert_equals(1,
            timeseries.get_index(UTCDateTime('2014-01-01T01:01:02'), True))

def test_length():
    """geomag.io.Timeseries_test.test_length()

    Construct a timeseries object with 4 samples per channel.
    Verify ``len(timeseries)`` returns 4
    """
    timeseries = Timeseries('OBS',
            {
                'H': [1, 2, 3, 4],
                'E': [2, 3, 4, 5],
                'Z': [3, 4, 5, 6],
                'F': [4, 5, 6, 7]
            },
            UTCDateTime('2014-01-01T01:01:01'),
            UTCDateTime('2014-01-01T01:01:04'))
    assert_equals(4, len(timeseries))


def test_rate_seconds():
    """geomag.io.Timeseries_test.test_rate_seconds()

    Construct a timeseries with 4 samples, and starttime and endtime
    at 01 and 04 seconds within the same minute.
    Verify ``timeseries.rate`` is 1 (hertz).
    """
    timeseries = Timeseries('OBS',
            {
                'H': [1, 2, 3, 4],
                'E': [2, 3, 4, 5],
                'Z': [3, 4, 5, 6],
                'F': [4, 5, 6, 7]
            },
            UTCDateTime('2014-01-01T01:01:01'),
            UTCDateTime('2014-01-01T01:01:04'))
    assert_equals(1, timeseries.rate)

def test_rate_minutes():
    """geomag.io.Timeseries_test.test_rate_minutes()

    Construct a timeseries with 4 samples, and starttime and endtime
    at 01 and 04 minutes within the same same.
    Verify ``timeseries.rate`` is 1/60 (hertz).
    """
    timeseries = Timeseries('OBS',
            {
                'H': [1, 2, 3, 4],
                'E': [2, 3, 4, 5],
                'Z': [3, 4, 5, 6],
                'F': [4, 5, 6, 7]
            },
            UTCDateTime('2014-01-01T01:01:00'),
            UTCDateTime('2014-01-01T01:04:00'))
    assert_equals(1.0 / 60.0, timeseries.rate)
