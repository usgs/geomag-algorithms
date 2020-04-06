from typing import Optional

from obspy import UTCDateTime
from pydantic import BaseModel

from .. import pydantic_utcdatetime


class Absolute(BaseModel):
    """Computed absolute and baseline measurement.

    Attributes
    ----------
    element: the absolute and baseline component.
    absolute: absolute measurement.
        nT or ?radians?
    baseline: baseline measurement.
        nT or ?radians?
    starttime: time of first measurement used.
    endtime: time of last measurement used.
    shift: used to correct polarity.
    valid: whether values are considered valid.
    """

    element: str
    absolute: Optional[float] = None
    baseline: Optional[float] = None
    starttime: Optional[UTCDateTime] = None
    endtime: Optional[UTCDateTime] = None
    shift: float = 0
    valid: bool = True

    def is_valid(self) -> bool:
        return (
            self.valid
            and self.absolute is not None
            and self.baseline is not None
            and self.element is not None
            and self.endtime is not None
            and self.starttime is not None
        )
