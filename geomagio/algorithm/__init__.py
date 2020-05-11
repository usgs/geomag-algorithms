"""
Geomag Algorithms module
"""
from __future__ import absolute_import

# base classes
from .Algorithm import Algorithm
from .AlgorithmException import AlgorithmException

# algorithms
from .AdjustedAlgorithm import AdjustedAlgorithm
from .AverageAlgorithm import AverageAlgorithm
from .DbDtAlgorithm import DbDtAlgorithm
from .DeltaFAlgorithm import DeltaFAlgorithm
from .FilterAlgorithm import FilterAlgorithm
from .SqDistAlgorithm import SqDistAlgorithm
from .XYZAlgorithm import XYZAlgorithm


# algorithms is used by Controller to auto generate arguments
algorithms = {
    "identity": Algorithm,
    "adjusted": AdjustedAlgorithm,
    "average": AverageAlgorithm,
    "dbdt": DbDtAlgorithm,
    "deltaf": DeltaFAlgorithm,
    "filter": FilterAlgorithm,
    "sqdist": SqDistAlgorithm,
    "xyz": XYZAlgorithm,
}


__all__ = [
    # base classes
    "Algorithm",
    "AlgorithmException",
    # algorithms
    "AdjustedAlgorithm",
    "AverageAlgorithm",
    "DbDtAlgorithm",
    "DeltaFAlgorithm",
    "FilterAlgorithm",
    "SqDistAlgorithm",
    "XYZAlgorithm",
]
