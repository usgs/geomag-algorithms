from geomagio.residual import SpreadsheetAbsolutesFactory
from numpy.testing import assert_almost_equal


def get_calculations():
    """
    Tests functionality of SpreadsheetAbsolutesFactory and recalculation of absolutes
    """
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    saf = SpreadsheetAbsolutesFactory()
    # Read spreadsheet containing test data
    reading = saf.parse_spreadsheet("etc/residual/DED-20140952332.xlsm")
    # establish original absolute object
    original = reading.absolutes_index()
    # recalculate absolute object using Calculation.py
    reading.update_absolutes()
    # establish recalculated absolute object
    result = reading.absolutes_index()


def test_DED_20140952332():
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of Dedhorse's metadata for use by calculations.
    Tests calculations for measurements in units of DMS.
    """
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    saf = SpreadsheetAbsolutesFactory()
    # Read spreadsheet containing test data
    reading = saf.parse_spreadsheet("etc/residual/DED-20140952332.xlsm")
    # establish original absolute object
    original = reading.absolutes_index()
    # recalculate absolute object using Calculation.py
    reading.update_absolutes()
    # establish recalculated absolute object
    result = reading.absolutes_index()
    assert_almost_equal(
        [original["H"].absolute, original["H"].baseline],
        [result["H"].absolute, result["H"].baseline],
        decimal=4,
        verbose=True,
    )
    assert_almost_equal(
        [original["D"].absolute, original["D"].baseline],
        [result["D"].absolute, result["D"].baseline],
        decimal=4,
        verbose=True,
    )
    assert_almost_equal(
        [original["Z"].absolute, original["Z"].baseline],
        [result["Z"].absolute, result["Z"].baseline],
        decimal=4,
        verbose=True,
    )


def test_BRW_20133650000():
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of BRW's metadata for use by calculations.
    Tests calculations for measurements in units of DM.
    """
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    saf = SpreadsheetAbsolutesFactory()
    # Read spreadsheet containing test data
    reading = saf.parse_spreadsheet("etc/residual/BRW-20133650000.xlsm")
    # establish original absolute object
    original = reading.absolutes_index()
    # recalculate absolute object using Calculation.py
    reading.update_absolutes()
    # establish recalculated absolute object
    result = reading.absolutes_index()
    assert_almost_equal(
        [original["H"].absolute, original["H"].baseline],
        [result["H"].absolute, result["H"].baseline],
        decimal=4,
        verbose=True,
    )
    assert_almost_equal(
        [original["D"].absolute, original["D"].baseline],
        [result["D"].absolute, result["D"].baseline],
        decimal=4,
        verbose=True,
    )
    assert_almost_equal(
        [original["Z"].absolute, original["Z"].baseline],
        [result["Z"].absolute, result["Z"].baseline],
        decimal=4,
        verbose=True,
    )
