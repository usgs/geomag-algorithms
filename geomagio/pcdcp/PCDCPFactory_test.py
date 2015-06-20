"""Tests for PCDCPFactory."""

from PCDCPFactory import PCDCPFactory
from obspy.core.utcdatetime import UTCDateTime
from nose.tools import assert_equals


def test__get_days():
    """geomagio.pcdcp.PCDCPFactory_test.test__get_days()

    Call the _get_days method with starttime and endtime separated by more
    than one day.
    Verify it returns all days between the given starttime and endtime.
    """
    starttime = UTCDateTime('2014-01-01')
    endtime = UTCDateTime('2014-01-07')

    assert_equals(PCDCPFactory('')._get_days(starttime, endtime), [
                UTCDateTime('2014-01-01'),
                UTCDateTime('2014-01-02'),
                UTCDateTime('2014-01-03'),
                UTCDateTime('2014-01-04'),
                UTCDateTime('2014-01-05'),
                UTCDateTime('2014-01-06'),
                UTCDateTime('2014-01-07')])
