"""Tests for the IAGA2002 Parser class."""

from numpy.testing import assert_equal
from geomagio.iaga2002 import IAGA2002Parser


IAGA2002_EXAMPLE = \
""" Format                 IAGA-2002                                    |
 Source of Data         United States Geological Survey (USGS)       |
 Station Name           Boulder Test                                 |
 IAGA CODE              BDT                                          |
 Geodetic Latitude      40.137                                       |
 Geodetic Longitude     254.764                                      |
 Elevation              1682                                         |
 Reported               HDZF                                         |
 Sensor Orientation     HDZF                                         |
 Digital Sampling       0.01 second                                  |
 Data Interval Type     filtered 1-minute (00:15-01:45)              |
 Data Type              variation                                    |
 # DECBAS               5527    (Baseline declination value in       |
 #                      tenths of minutes East (0-216,000)).         |
 # Vector 1-minute values are computed from 1-second values using    |
 # the INTERMAGNET gaussian filter centered on the minute.           |
 # Scalar 1-minute values are computed from 1-second values using    |
 # the INTERMAGNET gaussian filter centered on the minute.           |
 # This data file was constructed by the Golden GIN.                 |
 # Final data will be available on the INTERMAGNET DVD.              |
 # Go to www.intermagnet.org for details on obtaining this product.  |
 # CONDITIONS OF USE: The Conditions of Use for data provided        |
 # through INTERMAGNET and acknowledgement templates can be found    |
 # at www.intermagnet.org                                            |
DATE       TIME         DOY     BDTH      BDTD      BDTZ      BDTF   |
2013-09-01 00:00:00.000 244     21516.28    -29.03  47809.92  52533.39
2013-09-01 00:01:00.000 244     21516.55    -29.09  47809.75  52533.35
2013-09-01 00:02:00.000 244     21516.84    -29.14  47809.53  52533.28
2013-09-01 00:03:00.000 244     21515.48    -29.07  47809.49  52532.69
2013-09-01 00:04:00.000 244     21515.23    -29.02  47809.32  52532.43
2013-09-01 00:05:00.000 244     21515.49    -29.00  47809.26  52532.49
2013-09-01 00:06:00.000 244     21515.21    -28.99  47809.23  52532.33
2013-09-01 00:07:00.000 244     21514.81    -28.93  47809.14  52532.09
2013-09-01 00:08:00.000 244     21514.83    -28.87  47809.07  52532.04
2013-09-01 00:09:00.000 244     21515.04    -28.86  47809.04  52532.10"""


def test__merge_comments():
    """iaga2002_test.IAGA2002Parser_test.test_merge_comments()

    Call the _merge_comments method with 3 lines,
    only the middle line ending in a period.
    Verify, the first and second line are merged.
    """
    comments = ['line 1', 'line 2.', 'line 3']
    assert_equal(
        IAGA2002Parser()._merge_comments(comments),
        ['line 1 line 2.', 'line 3'])


def test__parse_header():
    """iaga2002_test.IAGA2002Parser_test.test_parse_header()

    Call the _parse_header method with a header.
    Verify the header name and value are split at the correct column.
    """
    parser = IAGA2002Parser()
    parser._parse_header(' Format                 ' +
            'IAGA-2002                                    |')
    assert_equal(parser.headers['Format'], 'IAGA-2002')


def test__parse_comment():
    """iaga2002_test.IAGA2002Parser_test.test_parse_header()

    Call the _parse_comment method with a comment.
    Verify the comment delimiters are removed.
    """
    parser = IAGA2002Parser()
    parser._parse_comment(' # Go to www.intermagnet.org for details on' +
            ' obtaining this product.  |')
    assert_equal(parser.comments[-1],
            'Go to www.intermagnet.org for details on' +
                    ' obtaining this product.')


def test__parse_channels():
    """iaga2002_test.IAGA2002Parser_test.test_parse_channels()

    Call the _parse_header method with an IAGA CODE header, then call
    the _parse_channels method with a channels header line.
    Verify the IAGA CODE value is removed from parsed channel names.
    """
    parser = IAGA2002Parser()
    parser._parse_header(' IAGA CODE              ' +
            'BDT                                          |')
    parser._parse_channels('DATE       TIME         DOY     ' +
            'BDTH      BDTD      BDTZ      BDTF   |')
    assert_equal(parser.channels, ['H', 'D', 'Z', 'F'])


def test_parse_decbas():
    """iaga2002_test.IAGA2002Parser_test.test_parse_decbas()

    Call the parse method with a portion of an IAGA 2002 File,
    which contains a DECBAS header comment.
    Verify DECBAS appears in the headers dict, with the expected value.
    """
    parser = IAGA2002Parser()
    parser.parse(IAGA2002_EXAMPLE)
    assert_equal(parser.metadata['declination_base'], 5527)
