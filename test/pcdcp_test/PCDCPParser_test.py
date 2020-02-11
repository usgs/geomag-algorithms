"""Tests for the PCDCP Parser class."""

from numpy.testing import assert_equal
from geomagio.pcdcp import PCDCPParser


PCDCP_EXAMPLE = \
"""
BOU  2015  001  01-Jan-15  HEZF  0.01nT  File Version 2.00
0000  2086167    -5707  4745737  5237768
0001  2086190    -5664  4745737  5237777
0002  2086213    -5638  4745741  5237787
0003  2086239    -5632  4745739  5237796
0004  2086198    -5626  4745743  5237786
0005  2086228    -5600  4745728  5237784
0006  2086242    -5578  4745725  5237787
0007  2086258    -5552  4745726  5237792
0008  2086278    -5571  4745734  5237808
"""

PCDCP_EXAMPLE_SECOND = \
"""
BOU  2015  001  01-Jan-15  HEZF  0.001nT  File Version 2.00
00000  20861520    -57095  47457409  52377630
00001  20861533    -57096  47457397  52377650
00002  20861554    -57077  47457391  52377650
00003  20861578    -57068  47457389  52377680
00004  20861600    -57068  47457384  52377660
00005  20861640    -57047  47457388  52377690
00006  20861654    -57039  47457378  52377650
00007  20861699    -57026  47457377  52377690
00008  20861721    -56995  47457365  52377680
00009  20861743    -56977  47457350  52377680
00010  20861750    -56968  47457349  52377690
"""


def test_parse_header():
    """pcdcp_test.PCDCPParser_test.test_parse_header()

    Call the _parse_header method with a header.
    Verify the header name and value are split at the correct column.
    """
    parser = PCDCPParser()
    parser._parse_header('BOU  2015  001  01-Jan-15  HEZF  0.01nT' +
        '  File Version 2.00')

    assert_equal(parser.header['date'], '01-Jan-15')
    assert_equal(parser.header['station'], 'BOU')
    assert_equal(parser.header['year'], '2015')
    assert_equal(parser.header['yearday'], '001')
    assert_equal(parser.header['resolution'], '0.01nT')


def test_parse_header_sec():
    """pcdcp_test.PCDCPParser_test.test_parse_header_sec()

    Call the _parse_header method with a pcdcp seconds file '.raw'
    header.  Verify the header name and value are split correctly.
    """
    parser = PCDCPParser()
    parser._parse_header('BOU  2015  001  01-Jan-15  HEZF  0.001nT' +
        ' File Version 2.00')

    assert_equal(parser.header['date'], '01-Jan-15')
    assert_equal(parser.header['station'], 'BOU')
    assert_equal(parser.header['year'], '2015')
    assert_equal(parser.header['yearday'], '001')
    assert_equal(parser.header['resolution'], '0.001nT')
