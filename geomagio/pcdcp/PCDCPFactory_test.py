"""Tests for PCDCPFactory."""

from PCDCPFactory import PCDCPFactory
from obspy.core.utcdatetime import UTCDateTime
from nose.tools import assert_equals


def test_parse_string():
    """geomagio.pcdcp.PCDCPFactory_test.test_parse_string()

    Send a PCDCP file string in to parse_string to make sure a well formed
    stream is created with proper values.
    """
    pcdcpString = "BOU  2015  001  01-Jan-15  HEZF  0.01nT  File Version 2.00\n"
                + "0000  2086167    -5707  4745737  5237768\n"
                + "0001  2086190    -5664  4745737  5237777\n"
                + "0002  2086213    -5638  4745741  5237787\n"
                + "0003  2086239    -5632  4745739  5237796\n"
                + "0004  2086198    -5626  4745743  5237786\n"

    stream = PCDCPFactory().parse_string(pcdcpString)

    assert_equals(type(stream), obspy.core.stream.Stream)
    assert_equals(stream[0].stats.network, 'NT')
    assert_equals(stream[0].stats.station, 'BOU')
    assert_equals(stream[0].stats.starttime,
                UTCDateTime('2015-01-01T00:00:00.000000Z'))
