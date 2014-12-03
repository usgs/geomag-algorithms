"""IO Module for IAGA 2002 Format

Based on documentation at:
  http://www.ngdc.noaa.gov/IAGA/vdat/iagaformat.html
"""

from IAGA2002Factory import IAGA2002Factory
from IAGA2002Parser import IAGA2002Parser
from MagWebFactory import MagWebFactory


__all__ = [
    'IAGA2002Factory',
    'IAGA2002Parser',
    'MagWebFactory'
]
