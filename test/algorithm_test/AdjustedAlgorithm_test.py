from geomagio.algorithm import AdjustedAlgorithm as adj
import geomagio.iaga2002 as i2
from numpy.testing import assert_almost_equal, assert_equal


def test_construct():
    """algorithm_test.AdjustedAlgorithm_test.test_construct()"""
    # load adjusted data transform matrix and pier correction
    a = adj(statefile="etc/adjusted/adjbou_state_.json")

    assert_almost_equal(actual=a.matrix[0, 0], desired=9.83427577e-01, decimal=6)

    assert_equal(actual=a.pier_correction, desired=-22)


def test_process_XYZF():
    """algorithm_test.AdjustedAlgorithm_test.test_process()

    Check adjusted data processing versus files generated from
    original script
    """
    # load adjusted data transform matrix and pier correction
    a = adj(statefile="etc/adjusted/adjbou_state_.json")

    # load boulder Jan 16 files from /etc/ directory
    with open("etc/adjusted/BOU201601vmin.min") as f:
        raw = i2.IAGA2002Factory().parse_string(f.read())
    with open("etc/adjusted/BOU201601adj.min") as f:
        expected = i2.IAGA2002Factory().parse_string(f.read())

    # process hezf (raw) channels with loaded transform
    adjusted = a.process(raw)

    # compare channels from adjusted and expected streams
    assert_almost_equal(
        actual=adjusted.select(channel="X")[0].data,
        desired=expected.select(channel="X")[0].data,
        decimal=2,
    )
    assert_almost_equal(
        actual=adjusted.select(channel="Y")[0].data,
        desired=expected.select(channel="Y")[0].data,
        decimal=2,
    )
    assert_almost_equal(
        actual=adjusted.select(channel="Z")[0].data,
        desired=expected.select(channel="Z")[0].data,
        decimal=2,
    )
    assert_almost_equal(
        actual=adjusted.select(channel="F")[0].data,
        desired=expected.select(channel="F")[0].data,
        decimal=2,
    )


def test_process_reverse_polarity():
    """algorithm_test.AdjustedAlgorithm_test.test_process()

    Check adjusted data processing versus files generated from
    original script. Tests reverse polarity martix.
    """
    # load adjusted data transform matrix and pier correction
    a = adj(
        statefile="etc/adjusted/adjbou_state_HE_.json",
        inchannels=["H", "E"],
        outchannels=["H", "E"],
    )

    # load boulder May 20 files from /etc/ directory
    with open("etc/adjusted/BOU202005vmin.min") as f:
        raw = i2.IAGA2002Factory().parse_string(f.read())
    with open("etc/adjusted/BOU202005adj.min") as f:
        expected = i2.IAGA2002Factory().parse_string(f.read())

    # process he(raw) channels with loaded transform
    adjusted = a.process(raw)

    # compare channels from adjusted and expected streams
    assert_almost_equal(
        actual=adjusted.select(channel="H")[0].data,
        desired=expected.select(channel="H")[0].data,
        decimal=2,
    )
    assert_almost_equal(
        actual=adjusted.select(channel="E")[0].data,
        desired=expected.select(channel="E")[0].data,
        decimal=2,
    )
