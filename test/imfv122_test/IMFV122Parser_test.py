"""Tests for the IMFV122 Parser class."""

from nose.tools import assert_equals
from geomagio.imfv122 import IMFV122Parser
from obspy.core import UTCDateTime


def test_imfv122_parse_header__hour_of_day():
    """imfv122_test.test_imfv122_parse_header__minutes.
    """
    parser = IMFV122Parser()
    parser._parse_header(
            'KAK MAY0216 123 03 HDZF A KYO 05381402 000000 RRRRRRRRRRRRRRRR')
    assert_equals(parser.channels, ['H', 'D', 'Z', 'F'])
    metadata = parser.metadata
    assert_equals(metadata['declination_base'], 0)
    assert_equals(metadata['geodetic_latitude'], 53.8)
    assert_equals(metadata['geodetic_longitude'], 140.2)
    assert_equals(metadata['station'], 'KAK')
    assert_equals(parser._delta, 60)
    assert_equals(parser._nexttime, UTCDateTime('2016-05-02T03:00:00Z'))


def test_imfv122_parse_header__minute_of_day():
    """imfv122_test.test_imfv122_parse_header__seconds.
    """
    parser = IMFV122Parser()
    parser._parse_header(
            'HER JAN0116 001 0123 HDZF R EDI 12440192 -14161 DRRRRRRRRRRRRRRR')
    assert_equals(parser.channels, ['H', 'D', 'Z', 'F'])
    metadata = parser.metadata
    assert_equals(metadata['declination_base'], -14161)
    assert_equals(metadata['geodetic_latitude'], 124.4)
    assert_equals(metadata['geodetic_longitude'], 19.2)
    assert_equals(metadata['station'], 'HER')
    assert_equals(parser._delta, 60)
    assert_equals(parser._nexttime, UTCDateTime('2016-01-01T02:03:00Z'))


def test_imfv122_parse_data():
    """imfv122_test.test_imfv122_parse_data.
    """
    parser = IMFV122Parser()
    parser._parse_header(
            'HER JAN0116 001 0123 HDZF R EDI 12440192 -14161 DRRRRRRRRRRRRRRR')
    parser._parse_data('1234 5678 9101 1121 3141 5161 7181 9202')
    import pprint
    pprint.pprint(parser._parsedata)
    assert_equals(parser._parsedata[0][0], UTCDateTime('2016-01-01T02:03:00Z'))
    assert_equals(parser._parsedata[1][0], '1234')
    assert_equals(parser._parsedata[2][0], '5678')
    assert_equals(parser._parsedata[3][0], '9101')
    assert_equals(parser._parsedata[4][0], '1121')
    assert_equals(parser._parsedata[0][1], UTCDateTime('2016-01-01T02:04:00Z'))
    assert_equals(parser._parsedata[1][1], '3141')
    assert_equals(parser._parsedata[2][1], '5161')
    assert_equals(parser._parsedata[3][1], '7181')
    assert_equals(parser._parsedata[4][1], '9202')


def test_imfv122_post_process():
    """imfv122_test.test_imfv122_post_process.
    """
    parser = IMFV122Parser()
    parser._parse_header(
            'HER JAN0116 001 0123 HDZF R EDI 12440192 -14161 DRRRRRRRRRRRRRRR')
    parser._parse_data('1234 5678 9101 1121 3141 5161 7181 9202')
    parser._post_process()
    assert_equals(parser.times[0], UTCDateTime('2016-01-01T02:03:00Z'))
    assert_equals(parser.data['H'][0], 123.4)
    assert_equals(parser.data['D'][0], 56.78)
    assert_equals(parser.data['Z'][0], 910.1)
    assert_equals(parser.data['F'][0], 112.1)
    assert_equals(parser.times[1], UTCDateTime('2016-01-01T02:04:00Z'))
    assert_equals(parser.data['H'][1], 314.1)
    assert_equals(parser.data['D'][1], 51.61)
    assert_equals(parser.data['Z'][1], 718.1)
    assert_equals(parser.data['F'][1], 920.2)
