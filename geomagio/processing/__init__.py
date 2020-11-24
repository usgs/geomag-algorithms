"""Package with near-real time processing configurations.

Note that these implementations are subject to change,
and should be considered less stable than other packages in the library.
"""
from .factory import get_edge_factory, get_miniseed_factory
from .observatory import adjusted, average, deltaf, rotate, sqdist_minute
from .obsrio import obsrio_minute, obsrio_second, obsrio_temperatures, obsrio_tenhertz


__all__ = [
    "adjusted",
    "average",
    "deltaf",
    "get_edge_factory",
    "get_miniseed_factory",
    "obsrio_minute",
    "obsrio_second",
    "obsrio_temperatures",
    "obsrid_tenhertz",
    "rotate",
    "sqdist_minute",
]
