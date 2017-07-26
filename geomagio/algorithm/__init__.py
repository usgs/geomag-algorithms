"""
Geomag Algorithms module
"""
from __future__ import absolute_import

# base classes
from .Algorithm import Algorithm
from .AlgorithmException import AlgorithmException
# algorithms
from .AdjustedAlgorithm import AdjustedAlgorithm
from .DeltaFAlgorithm import DeltaFAlgorithm
from .SqDistAlgorithm import SqDistAlgorithm
from .XYZAlgorithm import XYZAlgorithm
from .AverageAlgorithm import AverageAlgorithm


# algorithms is used by Controller to auto generate arguments
algorithms = {
    'identity': Algorithm,
    'adjusted': AdjustedAlgorithm,
    'average': AverageAlgorithm,
    'deltaf': DeltaFAlgorithm,
    'sqdist': SqDistAlgorithm,
    'xyz': XYZAlgorithm
}


__all__ = [
    # base classes
    'Algorithm',
    'AlgorithmException',
    # algorithms
    'AdjustedAlgorithm',
    'AverageAlgorithm',
    'DeltaFAlgorithm',
    'SqDistAlgorithm',
    'XYZAlgorithm'
]
