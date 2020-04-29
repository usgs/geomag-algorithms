import collections
from typing import Dict, List, Optional
from typing_extensions import Literal

from pydantic import BaseModel

from .Absolute import Absolute
from .Measurement import AverageMeasurement, Measurement, average_measurement
from .MeasurementType import MeasurementType


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

    absolutes: List[Absolute] = []
    azimuth: float = 0
    hemisphere: Literal[-1, 1] = 1
    measurements: List[Measurement] = []
    metadata: Dict = {}
    pier_correction: float = 0
    scale_value: float = None

    def __getitem__(self, measurement_type: MeasurementType):
        """Provide access to measurements by type.

        Example: reading[MeasurementType.WEST_DOWN]
        """
        return [m for m in self.measurements if m.measurement_type == measurement_type]
