"""Tests for the IMFV283 Parser class."""

from nose.tools import assert_equals
from IMFV283Parser import IMFV283Parser

import imfv283_codes


IMFV283_EXAMPLE_VIC = '75C2A3A814023012741G43-1NN027EUP00191`A^P@RVxZ}|' + \
    'D@@B_BEM@@@@@@@@@@@@@@@@@@@@@@@@@@@E|BxtTADVD@\E\BxxT@tVCh\\E' + \
    'lByDT@xVCp\\EdBy@T@tVCh\EhByPT@xVCl\\EPBy@T@tVCd\EdBxlTA@VCp\\Eh' + \
    'BxTTA@VCp\\EdBGxTA@VCl\EPBG`T@xVC\\\\DtBGHT@lVCD\DPBG@T@XVBh\\'

IMFV283_EXAMPLE_FRD = '75C2102614023012927G43-0NN027EUP00191bx@WyhD{' + \
    'aDB~@X@{Bb@@@@@@@@@@@@@@@@@@@@@@@@@@@@[DAV[@cUAjT@[EAVZ@cUAjT@[' + \
    'BAVZ@cVAjS@[DAVZ@cUAjS@[DAVZ@cUAjS@[GAV\\@cTAjT@[DAV[@cUAjT@[BAVY' + \
    '@cVAjT@[CAVW@cWAjT@[CAVT@cWAjU@[AAVO@cYAjV@Z}AVK@c[AjV'


def test_parse_msg_header():
    """geomagio.imfv283.IMFV283Parser_test.test_parse_msg_header()

    Call the _parse_header method with a header.
    Verify the header name and value are split at the correct column.
    """
    header = IMFV283Parser()._parse_msg_header(IMFV283_EXAMPLE_VIC)
    assert_equals(header['obs'], 'VIC')


def test_parse_goes_header():
    goes_data = IMFV283Parser()._process_ness_block(IMFV283_EXAMPLE_VIC,
        imfv283_codes.OBSERVATORIES['VIC'],
        191)
    goes_header = IMFV283Parser()._parse_goes_header(goes_data)
    assert_equals(goes_header['day'], 23)
