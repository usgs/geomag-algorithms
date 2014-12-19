"""Tests for IAGA2002Factory."""

from IAGA2002Factory import IAGA2002Factory
from obspy.core.utcdatetime import UTCDateTime
from nose.tools import assert_equals


def test__get_days():
    """geomag.io.iaga2002.IAGA2002Factory_test.test__get_days()

    Call the _get_days method with starttime and endtime separated by more
    than one day.
    Verify it returns all days between the given starttime and endtime.
    """
    starttime = UTCDateTime('2014-01-01')
    endtime = UTCDateTime('2014-01-07')
    assert_equals(IAGA2002Factory('')._get_days(starttime, endtime), [
                UTCDateTime('2014-01-01'),
                UTCDateTime('2014-01-02'),
                UTCDateTime('2014-01-03'),
                UTCDateTime('2014-01-04'),
                UTCDateTime('2014-01-05'),
                UTCDateTime('2014-01-06'),
                UTCDateTime('2014-01-07')])
