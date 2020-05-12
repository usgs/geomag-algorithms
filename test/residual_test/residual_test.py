from numpy.testing import assert_almost_equal
import pytest

from obspy.core import UTCDateTime
from geomagio.residual import (
    calculate,
    Reading,
    SpreadsheetAbsolutesFactory,
    WebAbsolutesFactory,
)


def assert_readings_equal(expected: Reading, actual: Reading, decimal: int):
    """
    Compares calculation actuals to expected absolutes from spreadsheet
    """
    print(expected.json(exclude={"measurements", "metadata"}, indent=2))
    print(actual.json(exclude={"measurements", "metadata"}, indent=2))
    expected_absolutes = {a.element: a for a in expected.absolutes}
    actual_absolutes = {a.element: a for a in actual.absolutes}
    assert_almost_equal(
        [actual_absolutes["H"].absolute, actual_absolutes["H"].baseline],
        [expected_absolutes["H"].absolute, expected_absolutes["H"].baseline],
        decimal=decimal,
        verbose=True,
    )
    assert_almost_equal(
        [actual_absolutes["D"].absolute, actual_absolutes["D"].baseline],
        [expected_absolutes["D"].absolute, expected_absolutes["D"].baseline],
        decimal=decimal,
        verbose=True,
    )
    assert_almost_equal(
        [actual_absolutes["Z"].absolute, actual_absolutes["Z"].baseline],
        [expected_absolutes["Z"].absolute, expected_absolutes["Z"].baseline],
        decimal=decimal,
        verbose=True,
    )

    if expected.scale_value is not None:
        assert_almost_equal(
            actual.scale_value, expected.scale_value, decimal=1, verbose=True
        )


def get_null_absolutes(observatory, starttime, endtime):
    """
    Tests functionality of WebAbsolutesFactory and recalculation of absolutes
    """
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    waf = WebAbsolutesFactory()
    # Read spreadsheet containing test data
    readings = waf.get_readings(observatory, starttime, endtime)
    return readings


def get_spreadsheet_absolutes(path):
    """
    Tests functionality of SpreadsheetAbsolutesFactory and recalculation of absolutes
    """
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    saf = SpreadsheetAbsolutesFactory()
    # Read spreadsheet containing test data
    reading = saf.parse_spreadsheet(path=path)
    return reading


def test_DED_20140952332():
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of Dedhorse's metadata for use by calculations.
    Tests calculations for measurements in units of DMS.
    """
    # gather absolute from DED test data and recalculate
    reading = get_spreadsheet_absolutes(path="etc/residual/DED-20140952332.xlsm")
    # test results with original spreadsheet values
    assert_readings_equal(
        expected=reading, actual=calculate(reading=reading), decimal=2
    )


def test_BRW_20133650000():
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of BRW's metadata for use by calculations.
    Tests calculations for measurements in units of DM.
    """
    # gather absolute from DED test data and recalculate
    reading = get_spreadsheet_absolutes(path="etc/residual/BRW-20133650000.xlsm")
    # test results with original spreadsheet values
    assert_readings_equal(
        expected=reading,
        actual=calculate(reading=reading),
        decimal=1,  # change due to no longer rounding
    )


def test_BOU_20190702():
    """
    Compare calulations to original absolutes obejct from web absolutes.
    Tests gathering of BOU's metadata for use by calculations.
    Tests calculations for null method measurements in units of DM.
    """
    readings = get_null_absolutes(
        observatory="BOU",
        starttime=UTCDateTime("2019-07-02T00:00:00Z"),
        endtime=UTCDateTime("2019-07-03T00:00:00Z"),
    )
    for reading in readings:
        assert_readings_equal(
            expected=reading,
            actual=calculate(reading=reading, adjust_reference=False),
            decimal=1,
        )


def test_BOU_20200422():
    """
    Compare calulations to original absolutes obejct from web absolutes.
    Tests gathering of BOU's metadata for use by calculations.
    Tests calculations for null method measurements in units of DMS.
    """
    readings = get_null_absolutes(
        observatory="BOU",
        starttime=UTCDateTime("2020-04-22T00:00:00Z"),
        endtime=UTCDateTime("2020-04-23T00:00:00Z"),
    )
    for reading in readings:
        assert_readings_equal(
            expected=reading,
            actual=calculate(reading=reading, adjust_reference=False),
            decimal=0,
        )
