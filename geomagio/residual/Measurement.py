import collections
from typing import Dict, List, Optional

import numpy
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
    residual: Optional[float] = None
    time: Optional[UTCDateTime] = None
    h: Optional[float] = None
    e: Optional[float] = None
    z: Optional[float] = None
    f: Optional[float] = None


class AverageMeasurement(Measurement):
    endtime: Optional[UTCDateTime] = None


def average_measurement(
    measurements: List[Measurement], types: List[MeasurementType] = None
) -> AverageMeasurement:
    """Calculate average from multiple measurements.

    Parameters
    ----------
    measurements - source measurements for average
    types - optional list of types to include, default all

    Returns
    -------
    None - if no measurements
    Otherwise, average of matching measurements.
        Type is copied from first measurement.
    """
    if types:
        measurements = [m for m in measurements if m.measurement_type in types]
    if len(measurements) == 0:
        # no measurements to average
        return None
    starttime = safe_min([m.time.timestamp for m in measurements if m.time])
    endtime = safe_max([m.time.timestamp for m in measurements if m.time])
    measurement = AverageMeasurement(
        measurement_type=measurements[0].measurement_type,
        angle=safe_average([m.angle for m in measurements]),
        residual=safe_average([m.residual for m in measurements]) or 0.0,
        time=starttime and UTCDateTime(starttime) or None,
        endtime=endtime and UTCDateTime(endtime) or None,
        h=safe_average([m.h for m in measurements]),
        e=safe_average([m.e for m in measurements]),
        z=safe_average([m.z for m in measurements]),
        f=safe_average([m.f for m in measurements]),
    )
    return measurement


def measurement_index(
    measurements: List[Measurement],
) -> Dict[MeasurementType, List[Measurement]]:
    """Generate index of measurements keyed by MeasurementType.

    Any missing MeasurementType returns an empty list.
    There may be multiple measurements of each MeasurementType.
    """
    index = collections.defaultdict(list)
    for m in measurements:
        index[m.measurement_type].append(m)
    return index


def safe_average(l: List[Optional[float]]):
    values = l and [f for f in l if f] or None
    return values and numpy.nanmean(values) or None


def safe_max(l: List[Optional[float]]):
    values = l and [f for f in l if f] or None
    return values and numpy.nanmax(values) or None


def safe_min(l: List[Optional[float]]):
    values = l and [f for f in l if f] or None
    return values and numpy.nanmin(values) or None
