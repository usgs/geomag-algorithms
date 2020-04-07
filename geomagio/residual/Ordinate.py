from .MeasurementType import MeasurementType
from obspy.core import UTCDateTime
from typing import Optional
from pydantic import BaseModel
from .. import pydantic_utcdatetime


class Ordinate(BaseModel):
    """One variometer reading per channel. Gathered from each measurement time within a Reading.

    Attributes
    ----------
    measurement_type: type of measurement.
    h, e, z, f: one variometer reading for each channel per measurement
    """

    measurement_type: MeasurementType = None
    time: Optional[UTCDateTime] = None
    h: float = 0
    e: float = 0
    z: float = 0
    f: float = 0
