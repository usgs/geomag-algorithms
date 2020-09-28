"""Tests for the IMFV283 Parser class."""
from __future__ import unicode_literals

from numpy.testing import assert_equal
from obspy import UTCDateTime

from geomagio.imfv283 import IMFV283Parser, imfv283_codes


IMFV283_EXAMPLE_VIC = (
    b"75C2A3A814023012741G43-1NN027EUP00191`A^P@RVxZ}|"
    + b"D@@B_BEM@@@@@@@@@@@@@@@@@@@@@@@@@@@E|BxtTADVD@\\E\\BxxT@tVCh\\E"
    + b"lByDT@xVCp\\EdBy@T@tVCh\\EhByPT@xVCl\\EPBy@T@tVCd\\EdBxlTA@VCp\\Eh"
    + b"BxTTA@VCp\\EdBGxTA@VCl\\EPBG`T@xVC\\\\DtBGHT@lVCD\\DPBG@T@XVBh\\"
)

IMFV283_EXAMPLE_FRD = (
    b"75C2102614023012927G43-0NN027EUP00191bx@WyhD{"
    + b"aDB~@X@{Bb@@@@@@@@@@@@@@@@@@@@@@@@@@@@[DAV[@cUAjT@[EAVZ@cUAjT@["
    + b"BAVZ@cVAjS@[DAVZ@cUAjS@[DAVZ@cUAjS@[GAV\\@cTAjT@[DAV[@cUAjT@[BAVY"
    + b"@cVAjT@[CAVW@cWAjT@[CAVT@cWAjU@[AAVO@cYAjV@Z}AVK@c[AjV"
)

IMFV283_EXAMPLE_STJ = (
    b"75C1E7AC20259002641G44-3NN027EXE00191`@OA@BWGbx{"
    + b"x@@Bh\x7fD`@@@@@@@@@@@@@@@@@@@@@@@@@@@FDODdV}X_yxAGHODlV~L_z|AG"
    + b"tODPV\x7f@_{pAxLOC`V\x7fp_|pAxPOBdV@D`}dAxdOAxVAX`~lAx`O@|VAp`\x7fXAyDO@tVCd`@\\Bx`O\x7fXUC|`APByDO\x7fdUEd`AtBx`O~\\UEp`BXBGtO}PUFP`CHB \n75C1E7AC20259001441G44-3NN027EXE00191`@LA@BWGbx{x@@Bh\x7fD`@@@@@@@@@@@@@@@@@@@@@@@@@@@\x7fhN{XU\x7fh_zPA\x7fPN|pU~P_xxA\x7fDN}xU|p_GpA@dO@pV||_FtA@hOA\\Vz|_FDAADOAxV{\\_FpABXOCXV{T_F`ABxODTV{L_F|ACpODxV{x_GPADLODpV|X_GxADpODhV|x_xlAEHODdV|x_yHA \n75C1E7AC20259000241G44-3NN027EXE00191`@IAEfWGby{x@@Bh\x7fD`@@@@@@@@@@@@@@@@@@@@@@@@@@@BxO{pT|h@y|BC@O|XT|t@yhBCDO}DT{p@xpBBpO}dT{H@ydBB`O\x7fLTyh@FHBAPO@PUGL@CxBAHOB\\UFL@BLBADOD\\UCh@\x7fdA@LOEHUB|@~|A@pOGdUB`@}dA\x7fxNx\\UAd@|hA\x7flNytU@H@{PA \n75C1E7AC20258235041G45-3NN027EXE00191`@JAEbWGby{x@@Bh\x7fD`@@@@@@@@@@@@@@@@@@@@@@@@@@@C|O{hT~D@{PBC`O{HT}h@{PBCtO{\\T}|@{TBCXOztT}X@{TBDPO{xT~`@{TBCdO{`T}p@z|BC@OzxT|x@z|BCPO{HT}\\@{DBC\\O{@T}t@{XBC\\O{XT}|@{HBCTO{lT}h@zhBB|O{\\T}H@z\\B \n"
)


def test_parse_msg_header():
    """imfv283_test.IMFV283Parser_test.test_parse_msg_header()

    Call the _parse_header method with a header.
    Verify the header names and values are split at the correct columns.
    """
    header = IMFV283Parser()._parse_msg_header(IMFV283_EXAMPLE_VIC)
    assert_equal(header["daps_platform"], b"75C2A3A8")
    assert_equal(header["obs"], "VIC")
    assert_equal(header["transmission_time"], b"14023012741")
    assert_equal(header["data_len"], 191)


def test_parse_goes_header_VIC():
    """imfv283_test.IMFV283Parser_test.test_parse_goes_header_VIC()"""
    goes_data = IMFV283Parser()._process_ness_block(
        IMFV283_EXAMPLE_VIC, imfv283_codes.OBSERVATORIES["VIC"], 191
    )
    actual_goes_header = IMFV283Parser()._parse_goes_header(goes_data)

    expected_header = {
        "day": 23,
        "minute": 73,
        "offset": bytearray(b"\x96\x86\xbd\xc1"),
        "orient": 0.0,
        "scale": [1, 1, 1, 1],
    }

    assert_equal(actual_goes_header, expected_header)
    assert_equal(type(actual_goes_header["minute"]), int)


def test_parse_goes_header_STJ():
    """imfv283_test.IMFV283Parser_test.test_parse_goes_header_STJ()"""
    goes_data = IMFV283Parser()._process_ness_block(
        IMFV283_EXAMPLE_STJ, imfv283_codes.OBSERVATORIES["STJ"], 191
    )
    actual_goes_header = IMFV283Parser()._parse_goes_header(goes_data)

    expected_header = {
        "day": 259,
        "minute": 12,
        "offset": bytearray(b"\x97x\xb8\xbe"),
        "orient": 0.0,
        "scale": [1, 1, 1, 1],
    }

    assert_equal(actual_goes_header, expected_header)
    assert_equal(type(actual_goes_header["minute"]), int)


def test_estimate_data_time__correct_doy():
    """imfv283_test.IMFV283Parser_test.test_estimate_data_time__correct_doy()

    Use example goes packet from BOU station, with correct goes doy value.
    """
    parser = IMFV283Parser()
    # BOU aka normal
    transmission = b"17274013121"
    day = 274
    minute = 72
    (data_time, transmit_time, corrected) = parser._estimate_data_time(
        transmission, day, minute
    )
    assert_equal(data_time, UTCDateTime("2017-10-01T01:12:00Z"))
    assert_equal(transmit_time, UTCDateTime("2017-10-01T01:31:21Z"))
    assert_equal(corrected, False)


def test_estimate_data_time__incorrect_doy():
    """imfv283_test.IMFV283Parser_test.test_estimate_data_time__correct_doy()

    Use example goes packet from BLC station, with incorrect goes doy value.
    """
    parser = IMFV283Parser()
    # BLC aka 1999 rollover gps issue
    transmission = b"17274013241"
    day = 46
    minute = 78
    (data_time, transmit_time, corrected) = parser._estimate_data_time(
        transmission, day, minute
    )
    assert_equal(data_time, UTCDateTime("2017-10-01T01:18:00Z"))
    assert_equal(transmit_time, UTCDateTime("2017-10-01T01:32:41Z"))
    assert_equal(corrected, True)
