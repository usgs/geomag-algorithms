from typing import Optional

from obspy.core import UTCDateTime
from pydantic import BaseModel

from .. import pydantic_utcdatetime
from .MeasurementType import MeasurementType


class Measurement(BaseModel):
    """One angle and time measurement with optional residual.

    Attributes
    ----------
    measurement_type: type of measurement.
    angle: measured angle, decimal degrees.
    residual: residual at time of measurement.
    time: when measurement was taken.
    """

    measurement_type: MeasurementType
    angle: float = 0
    residual: float = None
    time: Optional[UTCDateTime] = None
    mask: bool = False
