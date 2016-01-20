"""
Geomag Algorithms module
"""

# base classes
from Algorithm import Algorithm
from AlgorithmException import AlgorithmException
# algorithms
from DeltaFAlgorithm import DeltaFAlgorithm
from XYZAlgorithm import XYZAlgorithm


# algorithms is used by Controller to auto generate arguments
algorithms = {
    'identity': Algorithm,
    'deltaf': DeltaFAlgorithm,
    'xyz': XYZAlgorithm
}


__all__ = [
    # base classes
    'Algorithm',
    'AlgorithmException',
    # algorithms
    'DeltaFAlgorithm',
    'XYZAlgorithm'
]
