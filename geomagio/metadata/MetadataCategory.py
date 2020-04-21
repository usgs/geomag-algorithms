from enum import Enum

# known category values as enumeration
class MetadataCategory(str, Enum):
    ADJUSTED_MATRIX = "adjusted-matrix"
    FLAG = "flag"
    INSTRUMENT = "instrument"
    OBSERVATORY = "observatory"
    READING = "reading"
