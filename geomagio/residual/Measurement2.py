from typing import Optional

from obspy.core import UTCDateTime
from .MeasurementType import MeasurementType


class Measurement(object):
    """One angle and time measurement with optional residual.

    Attributes
    ----------
    measurement_type: type of measurement.
    angle: measured angle, decimal degrees.
    residual: residual at time of measurement.
    time: when measurement was taken.
    """

    def __init__(
        self,
        measurement_type: MeasurementType,
        angle: float = 0,
        residual: float = 0,
        time: Optional[UTCDateTime] = None,
    ):
        self.measurement_type = measurement_type
        self.angle = angle
        self.residual = residual
        self.time = time
