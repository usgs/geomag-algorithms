"""
Geomag Algorithms module
"""

# base classes
from Algorithm import Algorithm
from AlgorithmException import AlgorithmException
# algorithms
from DeltaFAlgorithm import DeltaFAlgorithm
from SqDistAlgorithm import SqDistAlgorithm
from XYZAlgorithm import XYZAlgorithm
from AdjustedAlgorithm import AdjustedAlgorithm

# algorithms is used by Controller to auto generate arguments
algorithms = {
    'identity': Algorithm,
    'deltaf': DeltaFAlgorithm,
    'sqdist': SqDistAlgorithm,
    'xyz': XYZAlgorithm,
    'adjusted': AdjustedAlgorithm
}


__all__ = [
    # base classes
    'Algorithm',
    'AlgorithmException',
    # algorithms
    'DeltaFAlgorithm',
    'SqDistAlgorithm',
    'XYZAlgorithm'
    'AdjustedAlgorithm'
]
