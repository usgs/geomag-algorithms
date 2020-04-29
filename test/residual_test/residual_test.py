from numpy.testing import assert_almost_equal
import pytest

from geomagio.residual import calculate, SpreadsheetAbsolutesFactory


def assert_absolutes(original, result):
    """
    Compares calculation results to original absolutes from spreadsheet
    """
    assert_almost_equal(
        [original["H"].absolute, original["H"].baseline],
        [result["H"].absolute, result["H"].baseline],
        decimal=4,
        verbose=True,
    )
    assert_almost_equal(
        [original["D"].absolute, original["D"].baseline],
        [result["D"].absolute, result["D"].baseline],
        decimal=3,
        verbose=True,
    )
    assert_almost_equal(
        [original["Z"].absolute, original["Z"].baseline],
        [result["Z"].absolute, result["Z"].baseline],
        decimal=4,
        verbose=True,
    )


def compare_spreadsheet_absolutes(path):
    """
    Tests functionality of SpreadsheetAbsolutesFactory and recalculation of absolutes
    """
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    saf = SpreadsheetAbsolutesFactory()
    # Read spreadsheet containing test data
    reading = saf.parse_spreadsheet(path=path)
    # establish original absolute object
    original = {a.element: a for a in reading.absolutes}
    calculated = calculate(reading)
    result = {a.element: a for a in calculated.absolutes}
    return original, result


def test_DED_20140952332():
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of Dedhorse's metadata for use by calculations.
    Tests calculations for measurements in units of DMS.
    """
    # gather absolute from DED test data and recalculate
    original, result = compare_spreadsheet_absolutes(
        path="etc/residual/DED-20140952332.xlsm"
    )
    # test results with original spreadsheet values
    assert_absolutes(original, result)


def test_BRW_20133650000():
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of BRW's metadata for use by calculations.
    Tests calculations for measurements in units of DM.
    """
    # gather absolute from DED test data and recalculate
    original, result = compare_spreadsheet_absolutes(
        path="etc/residual/BRW-20133650000.xlsm"
    )
    # test results with original spreadsheet values
    assert_absolutes(original, result)
