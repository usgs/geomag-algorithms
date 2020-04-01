from .MeasurementType import MeasurementType
from obspy.core import UTCDateTime
from typing import Optional


class Ordinate(object):
    """One variometer reading per channel. Gathered from each measurement time within a Reading.

    Attributes
    ----------
    measurement_type: type of measurement.
    h, e, z, f: one variometer reading for each channel per measurement
    """

    # FIXME: Add a starttime and endtime
    def __init__(
        self,
        measurement_type: MeasurementType,
        time: Optional[UTCDateTime] = None,
        h: float = 0,
        e: float = 0,
        z: float = 0,
        f: float = 0,
    ):
        self.measurement_type = measurement_type
        self.h = h
        self.e = e
        self.z = z
        self.f = f
