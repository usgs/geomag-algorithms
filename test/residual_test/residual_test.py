from geomagio.residual import SpreadsheetAbsolutesFactory
from numpy.testing import assert_almost_equal
import pytest


class test_functions:
    @staticmethod
    def get_absolutes(tmp_path):
        """
        Tests functionality of SpreadsheetAbsolutesFactory and recalculation of absolutes
        """
        # establish SpreadsheetAbsolutesFactory for reading test data from Excel
        saf = SpreadsheetAbsolutesFactory()
        # Read spreadsheet containing test data
        reading = saf.parse_spreadsheet(path=tmp_path)
        # establish original absolute object
        original = reading.absolutes_index()
        # recalculate absolute object using Calculation.py
        reading.update_absolutes()
        # establish recalculated absolute object
        result = reading.absolutes_index()
        return original, result

    @staticmethod
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
            decimal=4,
            verbose=True,
        )
        assert_almost_equal(
            [original["Z"].absolute, original["Z"].baseline],
            [result["Z"].absolute, result["Z"].baseline],
            decimal=4,
            verbose=True,
        )


@pytest.fixture
def test_session():
    return test_functions


def test_DED_20140952332(test_session):
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of Dedhorse's metadata for use by calculations.
    Tests calculations for measurements in units of DMS.
    """
    # gather absolute from DED test data and recalculate
    original, result = test_session.get_absolutes(
        tmp_path="etc/residual/DED-20140952332.xlsm"
    )
    # test results with original spreadsheet values
    test_session.assert_absolutes(original, result)


def test_BRW_20133650000(test_session):
    """
    Compare calulations to original absolutes obejct from Spreadsheet.
    Tests gathering of BRW's metadata for use by calculations.
    Tests calculations for measurements in units of DM.
    """
    # gather absolute from BRW test data and recalculate
    original, result = test_session.get_absolutes(
        tmp_path="etc/residual/BRW-20133650000.xlsm"
    )
    # test results with original spreadsheet values
    test_session.assert_absolutes(original, result)
