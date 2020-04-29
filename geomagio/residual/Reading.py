import collections
from typing import Dict, List, Optional
from typing_extensions import Literal

from obspy import Stream
from pydantic import BaseModel

from .. import TimeseriesUtility
from ..TimeseriesFactory import TimeseriesFactory
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
    scale_value: scale value in decimal degrees.
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

    def load_ordinates(
        self,
        observatory: str,
        timeseries_factory: TimeseriesFactory,
        default_existing: bool = True,
    ):
        """Load ordinates from a timeseries factory.

        Parameters
        ----------
        observatory: the observatory to load.
        timeseries_factory: source of data.
        default_existing: keep existing values if data not found.
        """
        mean = average_measurement(self.measurements)
        data = timeseries_factory.get_timeseries(
            observatory=observatory,
            channels=("H", "E", "Z", "F"),
            interval="second",
            type="variation",
            starttime=mean.time,
            endtime=mean.endtime,
        )
        self.update_measurement_ordinates(data, default_existing)

    def update_measurement_ordinates(self, data: Stream, default_existing: bool = True):
        """Update ordinates.

        Parameters
        ----------
        data: source of data.
        default_existing: keep existing values if data not found.
        """
        for measurement in self.measurements:
            if not measurement.time:
                continue
            measurement.h = TimeseriesUtility.get_trace_value(
                traces=data.select(channel="H"),
                time=measurement.time,
                default=default_existing and measurement.h or None,
            )
            measurement.e = TimeseriesUtility.get_trace_value(
                traces=data.select(channel="E"),
                time=measurement.time,
                default=default_existing and measurement.e or None,
            )
            measurement.z = TimeseriesUtility.get_trace_value(
                traces=data.select(channel="Z"),
                time=measurement.time,
                default=default_existing and measurement.z or None,
            )
            measurement.f = TimeseriesUtility.get_trace_value(
                traces=data.select(channel="F"),
                time=measurement.time,
                default=default_existing and measurement.f or None,
            )
