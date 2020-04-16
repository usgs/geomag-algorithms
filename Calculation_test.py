from geomagio.residual import SpreadsheetAbsolutesFactory
from numpy.testing import assert_almost_equal

import os


for filename in os.listdir("etc/residual"):
    if filename == ".DS_Store":
        continue
    # establish SpreadsheetAbsolutesFactory for reading test data from Excel
    saf = SpreadsheetAbsolutesFactory()
    # Read spreadsheet containing test data
    reading = saf.parse_spreadsheet("etc/residual/" + filename)
    # establish original absolute object
    original = reading.absolutes
    # recalculate absolute object using Calculation.py
    reading.update_absolutes()
    # establish recalculated absolute object
    result = reading.absolutes

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
            decimal=2,
            err_msg="Absolutes not within 4 decimals",
            verbose=True,
        )
        # test baseline values
        assert_almost_equal(
            o_baseline,
            r_baseline,
            decimal=2,
            err_msg="Baselines not within 4 decimals",
            verbose=True,
        )
