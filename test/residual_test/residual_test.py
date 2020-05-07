from numpy.testing import assert_almost_equal
import pytest

from geomagio.residual import calculate, Reading, SpreadsheetAbsolutesFactory


def assert_readings_equal(expected: Reading, actual: Reading):
    """
    Compares calculation actuals to expected absolutes from spreadsheet
    """
    expected_absolutes = {a.element: a for a in expected.absolutes}
    actual_absolutes = {a.element: a for a in actual.absolutes}
    assert_almost_equal(
        [expected_absolutes["H"].absolute, expected_absolutes["H"].baseline],
        [actual_absolutes["H"].absolute, actual_absolutes["H"].baseline],
        decimal=1,
        verbose=True,
    )
    assert_almost_equal(
        [expected_absolutes["D"].absolute, expected_absolutes["D"].baseline],
        [actual_absolutes["D"].absolute, actual_absolutes["D"].baseline],
        decimal=1,
        verbose=True,
    )
    assert_almost_equal(
        [expected_absolutes["Z"].absolute, expected_absolutes["Z"].baseline],
        [actual_absolutes["Z"].absolute, actual_absolutes["Z"].baseline],
        decimal=1,
        verbose=True,
    )
    assert_almost_equal(
        expected.scale_value, actual.scale_value, decimal=1, verbose=True
    )


def compare_spreadsheet_absolutes(path):
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
    reading = compare_spreadsheet_absolutes(path="etc/residual/DED-20140952332.xlsm")
    # test results with original spreadsheet values
    assert_readings_equal(reading, calculate(reading))


def test_BRW_20133650000():
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of BRW's metadata for use by calculations.
    Tests calculations for measurements in units of DM.
    """
    # gather absolute from DED test data and recalculate
    reading = compare_spreadsheet_absolutes(path="etc/residual/BRW-20133650000.xlsm")
    # test results with original spreadsheet values
    assert_readings_equal(reading, calculate(reading))
