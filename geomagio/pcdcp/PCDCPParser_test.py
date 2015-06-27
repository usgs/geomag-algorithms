"""Tests for the PCDCP Parser class."""

from nose.tools import assert_equals
from PCDCPParser import PCDCPParser


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


def test__parse_header():
    """geomagio.pcdcp.PCDCPParser_test.test_parse_header()

    Call the _parse_header method with a header.
    Verify the header name and value are split at the correct column.
    """
    parser = PCDCPParser()
    parser._parse_header('BOU  2015  001  01-Jan-15  HEZF  0.01nT' +
            '  File Version 2.00')

    assert_equals(parser.header['date'], '01-Jan-15')
    assert_equals(parser.header['station'], 'BOU')
    assert_equals(parser.header['year'], '2015')
    assert_equals(parser.header['yearday'], '001')
