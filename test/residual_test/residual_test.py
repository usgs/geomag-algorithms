from geomagio.residual import SpreadsheetAbsolutesFactory
from numpy.testing import assert_almost_equal

import os


def test_calculations():
    """
    Tests functionality of SpreadsheetAbsolutesFactory and recalculation of absolutes
    """
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    saf = SpreadsheetAbsolutesFactory()
    # Read spreadsheet containing test data
    reading = saf.parse_spreadsheet("etc/residual/DED-20140952332.xlsm")
    # establish original absolute object
    original = reading.absolutes
    # recalculate absolute object using Calculation.py
    reading.update_absolutes()
    # establish recalculated absolute object
    result = reading.absolutes


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
    original = reading.absolutes
    # recalculate absolute object using Calculation.py
    reading.update_absolutes()
    # establish recalculated absolute object
    result = reading.absolutes
    # run test for comparison of results to original data given by spreadsheet
    for i in range(len(result)):
        original_element = original[i]
        result_element = result[i]
        # gather elements' absolutes
        o_absolute = original_element.absolute
        r_absolute = result_element.absolute
        # gather element's baselines
        o_baseline = original_element.baseline
        r_baseline = result_element.baseline
        # test absolute values
        assert_almost_equal(
            o_absolute,
            r_absolute,
            decimal=4,
            err_msg="Absolutes not within 4 decimals",
            verbose=True,
        )
        # test baseline values
        assert_almost_equal(
            o_baseline,
            r_baseline,
            decimal=4,
            err_msg="Baselines not within 4 decimals",
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
    original = reading.absolutes
    # recalculate absolute object using Calculation.py
    reading.update_absolutes()
    # establish recalculated absolute object
    result = reading.absolutes
    # run test for comparison of results to original data given by spreadsheet
    for i in range(len(result)):
        original_element = original[i]
        result_element = result[i]
        # gather elements' absolutes
        o_absolute = original_element.absolute
        r_absolute = result_element.absolute
        # gather element's baselines
        o_baseline = original_element.baseline
        r_baseline = result_element.baseline
        # test absolute values
        assert_almost_equal(
            o_absolute, r_absolute, decimal=2, verbose=True,
        )
        # test baseline values
        assert_almost_equal(
            o_baseline, r_baseline, decimal=2, verbose=True,
        )
