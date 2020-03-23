import collections
from typing import Dict, List, Optional

from pydantic import BaseModel

from .Absolute import Absolute
from .Measurement import Measurement
from .MeasurementType import MeasurementType
from .Ordinate import Ordinate
from .Calculation import (
    calculate_scale,
    calculate_I,
    calculate_baselines,
    calculate_absolutes,
    calculate_D,
)


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
    hemisphere: float = 1  # maybe hemisphere should be calculated from latitude
    measurements: Optional[List[Measurement]] = []
    metadata: Optional[Dict] = []
    pier_correction: float = 0

    def absolutes_index(self) -> Dict[str, Absolute]:
        """Generate index of absolutes keyed by element.
        """
        return {a.element: a for a in self.absolutes}

    def calculate(self):
        # calculate inclination
        inclination, f, ordinate = calculate_I(
            self.measurement_index(),
            self.ordinates,
            self.ordinate_index(),
            self.metadata,
        )
        # calculate absolutes
        Habs, Zabs, Fabs = calculate_absolutes(
            f, inclination, self.metadata["pier_correction"]
        )
        # calculate baselines
        Hb, Zb = calculate_baselines(Habs, Zabs, ordinate)
        # calculate scale value for declination
        scale = calculate_scale(
            f, self.measurements, inclination, self.metadata["pier_correction"]
        )
        # calculate declination
        declination_baseline = calculate_D(
            self.ordinate_index(),
            self.measurements,
            self.measurement_index(),
            self.metadata["mark_azimuth"],
            Hb,
        )
        return Hb, Zb, declination_baseline, scale

    def measurement_index(self) -> Dict[MeasurementType, List[Measurement]]:
        """Generate index of measurements keyed by MeasurementType.

        Any missing MeasurementType returns an empty list.
        There may be multiple measurements of each MeasurementType.
        """
        index = collections.defaultdict(list)
        for m in self.measurements:
            index[m.measurement_type].append(m)
        return index

    def ordinate_index(self) -> Dict[MeasurementType, List[Ordinate]]:
        """Generate index of ordinates keyed by MeasurementType.

        Any missing MeasurementType returns an empty list.
        There may be multiple ordinates of each MeasurementType.
        """
        index = collections.defaultdict(list)
        for o in self.ordinates:
            index[o.measurement_type].append(o)
        return index
