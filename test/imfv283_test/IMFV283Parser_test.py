"""Tests for the IMFV283 Parser class."""

from nose.tools import assert_equals
from obspy import UTCDateTime

from geomagio.imfv283 import IMFV283Parser, imfv283_codes


IMFV283_EXAMPLE_VIC = '75C2A3A814023012741G43-1NN027EUP00191`A^P@RVxZ}|' + \
    'D@@B_BEM@@@@@@@@@@@@@@@@@@@@@@@@@@@E|BxtTADVD@\\E\BxxT@tVCh\\E' + \
    'lByDT@xVCp\\EdBy@T@tVCh\\EhByPT@xVCl\\EPBy@T@tVCd\\EdBxlTA@VCp\\Eh' + \
    'BxTTA@VCp\\EdBGxTA@VCl\\EPBG`T@xVC\\\\DtBGHT@lVCD\DPBG@T@XVBh\\'

IMFV283_EXAMPLE_FRD = '75C2102614023012927G43-0NN027EUP00191bx@WyhD{' + \
    'aDB~@X@{Bb@@@@@@@@@@@@@@@@@@@@@@@@@@@@[DAV[@cUAjT@[EAVZ@cUAjT@[' + \
    'BAVZ@cVAjS@[DAVZ@cUAjS@[DAVZ@cUAjS@[GAV\\@cTAjT@[DAV[@cUAjT@[BAVY' + \
    '@cVAjT@[CAVW@cWAjT@[CAVT@cWAjU@[AAVO@cYAjV@Z}AVK@c[AjV'


def test_parse_msg_header():
    """imfv283_test.IMFV283Parser_test.test_parse_msg_header()

    Call the _parse_header method with a header.
    Verify the header name and value are split at the correct column.
    """
    header = IMFV283Parser()._parse_msg_header(IMFV283_EXAMPLE_VIC)
    assert_equals(header['obs'], 'VIC')


def test_parse_goes_header():
    """imfv283_test.IMFV283Parser_test.test_parse_goes_header()
    """
    goes_data = IMFV283Parser()._process_ness_block(IMFV283_EXAMPLE_VIC,
        imfv283_codes.OBSERVATORIES['VIC'],
        191)
    goes_header = IMFV283Parser()._parse_goes_header(goes_data)
    assert_equals(goes_header['day'], 23)


def test_estimate_data_time__correct_doy():
    """imfv283_test.IMFV283Parser_test.test_estimate_data_time__correct_doy()

    Use example goes packet from BOU station, with correct goes doy value.
    """
    parser = IMFV283Parser()
    # BOU aka normal
    transmission = '17274013121'
    day = 274
    minute = 72
    (data_time, transmit_time, corrected) = \
            parser._estimate_data_time(transmission, day, minute)
    assert_equals(data_time, UTCDateTime('2017-10-01T01:12:00Z'))
    assert_equals(transmit_time, UTCDateTime('2017-10-01T01:31:21Z'))
    assert_equals(corrected, False)


def test_estimate_data_time__incorrect_doy():
    """imfv283_test.IMFV283Parser_test.test_estimate_data_time__correct_doy()

    Use example goes packet from BLC station, with incorrect goes doy value.
    """
    parser = IMFV283Parser()
    # BLC aka 1999 rollover gps issue
    transmission = '17274013241'
    day = 46
    minute = 78
    (data_time, transmit_time, corrected) = \
            parser._estimate_data_time(transmission, day, minute)
    assert_equals(data_time, UTCDateTime('2017-10-01T01:18:00Z'))
    assert_equals(transmit_time, UTCDateTime('2017-10-01T01:32:41Z'))
    assert_equals(corrected, True)
