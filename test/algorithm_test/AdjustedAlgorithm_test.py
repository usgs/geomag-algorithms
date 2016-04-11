from geomagio.algorithm import AdjustedAlgorithm as adj
# import numpy as np
from nose.tools import assert_equals
from nose.tools import assert_almost_equals


def test_construct():
    """
    path to
    """
    matrix = None
    pier_correction = None
    a = adj.AdjustedAlgorithm(matrix, pier_correction,
        'etc/adjusted/adjbou_state_.json')

    assert_almost_equals(a.matrix[0, 0], 9.83427577e-01, 6)

    assert_equals(a.pier_correction, -22)


def test_trivial():
    """
    """

    assert_equals(3, 3)
