"""Tests for PCDCPFactory."""

from geomagio.pcdcp import PCDCPFactory
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.stream import Stream
from numpy.testing import assert_equal

pcdcpString = \
"""BOU  2015  001  01-Jan-15  HEZF  0.01nT  File Version 2.00
0000  2086167    -5707  4745737  5237768
0001  2086190    -5664  4745737  5237777
0002  2086213    -5638  4745741  5237787
0003  2086239    -5632  4745739  5237796
0004  2086198    -5626  4745743  5237786"""

pcdcpString_seconds = \
"""BOU  2015  001  01-Jan-15  HEZF  0.001nT  File Version 2.00
00000  20861520    -57095  47457409  52377630
00001  20861533    -57096  47457397  52377650
00002  20861554    -57077  47457391  52377650
00003  20861578    -57068  47457389  52377680
00004  20861600    -57068  47457384  52377660
"""


def test_parse_string():
    """pcdcp_test.PCDCPFactory_test.test_parse_string()

    Send a PCDCP file string in to parse_string to make sure a well formed
    stream is created with proper values.
    """
    stream = PCDCPFactory().parse_string(pcdcpString)

    assert_equal(type(stream), Stream)
    assert_equal(stream[0].stats.network, 'NT')
    assert_equal(stream[0].stats.station, 'BOU')
    assert_equal(stream[0].stats.starttime,
                UTCDateTime('2015-01-01T00:00:00.000000Z'))
    h = stream.select(channel='H')[0]
    assert_equal(h.data[1], 20861.90)
    assert_equal(stream[0].stats.endtime,
                UTCDateTime('2015-01-01T00:04:00.000000Z'))
    z = stream.select(channel='Z')[0]
    assert_equal(z.data[-1], 47457.43)


def test_parse_string_seconds():
    """pcdcp_test.PCDCPFactory_test.test_parse_string_seconds()

    Send a PCDCP seconds file string into parse_string to make sure a well
    formed stream is created with proper values
    """
    stream = PCDCPFactory().parse_string(pcdcpString_seconds)

    assert_equal(type(stream), Stream)
    assert_equal(stream[0].stats.network, 'NT')
    assert_equal(stream[0].stats.station, 'BOU')
    assert_equal(stream[0].stats.starttime,
                UTCDateTime('2015-01-01T00:00:00.000000Z'))
    h = stream.select(channel='H')[0]
    assert_equal(h.data[0], 20861.520)
    assert_equal(stream[0].stats.endtime,
                UTCDateTime('2015-01-01T00:00:04.000000Z'))
    z = stream.select(channel='Z')[0]
    assert_equal(z.data[-1], 47457.384)
