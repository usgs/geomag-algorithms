import collections
from typing import Dict, List, Optional

from pydantic import BaseModel

from .Absolute import Absolute
from .Measurement import AverageMeasurement, Measurement, average_measurement
from .MeasurementType import MeasurementType
from .Calculation import calculate


class Reading(BaseModel):
    """A collection of absolute measurements.

    Attributes
    ----------
    absolutes: absolutes computed from measurements.
    azimuth: azimuth angle to mark used for measurements, decimal degrees.
    hemisphere: 1 for northern hemisphere, -1 for southern hemisphere
    measurements: raw measurements used to compute absolutes.
    metadata: metadata used during absolute calculations.
    pier_correction: pier correction value, nT.
    """

    absolutes: Optional[List[Absolute]] = None
    azimuth: float = 0
    hemisphere: float = 1
    measurements: Optional[List[Measurement]] = []
    metadata: Optional[Dict] = []
    pier_correction: float = 0

    def get_average(self, types: List[MeasurementType]) -> AverageMeasurement:
        return average_measurement(
            [m for m in self.measurements if m.measurement_type in types]
        )

    def update_absolutes(self):
        self.absolutes = calculate(self)
        return self.absolutes
