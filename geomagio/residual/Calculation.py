from typing import List, Tuple

import numpy as np
from pydantic import BaseModel

from .Absolute import Absolute
from .Angle import from_dms, to_dms
from .MeasurementType import MeasurementType as mt
from .Measurement import (
    AverageMeasurement,
    Measurement,
    average_measurement,
    measurement_index,
)


# specify mark measurement types
MARK_TYPES = [
    mt.FIRST_MARK_DOWN,
    mt.FIRST_MARK_UP,
    mt.SECOND_MARK_DOWN,
    mt.SECOND_MARK_UP,
]

# define measurement types used to calculate inclination
INCLINATION_TYPES = [mt.NORTH_DOWN, mt.NORTH_UP, mt.SOUTH_DOWN, mt.SOUTH_UP]

# define measurement types used to calculate declination
DECLINATION_TYPES = [mt.EAST_UP, mt.EAST_DOWN, mt.WEST_UP, mt.WEST_DOWN]


def calculate(reading) -> Tuple[Absolute, Absolute, Absolute]:
    """
    Calculate/recalculate absolute from a Reading object's
    ordinates, measurements, and metadata.
    Outputs a list of absolutes containing baseline, absolute,
    and element name. Also reutrns the scale value.
    """
    # gather oridinates, measuremenets, and metadata objects from reading
    index = measurement_index(reading.measurements)
    # reference measurement, used to adjust absolutes
    reference = index[mt.WEST_DOWN][0]
    # calculate inclination
    inclination, f, mean = calculate_I(reading)
    # calculate absolutes
    absoluteH, absoluteZ = calculate_HZ_absolutes(inclination, f, mean, reference)
    scale_value = calculate_scale(inclination, f, index[mt.NORTH_DOWN_SCALE])
    # calculate declination absolute and baseline
    absoluteD = calculate_D_absolute(reading, absoluteH, reference)
    return absoluteD, absoluteH, absoluteZ


def calculate_I(reading) -> Tuple[float, float, Measurement]:
    """
    Calculate inclination angles from measurements, ordinates,
    average ordinates from every measurement, and metadata.
    Returns inclination angle and calculated average f
    """
    index = measurement_index(reading.measurements)
    # mean across all inclination measurements
    mean = reading.get_average(INCLINATION_TYPES)
    # mean within each type
    measurements = [reading.get_average(t) for t in INCLINATION_TYPES]
    # get initial inclination angle, assumed to be the southdown angle
    inclination = reading.get_average([mt.NORTH_UP]).angle
    if inclination >= 90:
        inclination -= 180
    # loop until inclination converges
    last_inclination = inclination + 1
    while abs(last_inclination - inclination) > 0.0001:
        # set temporary inclination variable to hold previous step's inclination
        last_inclination = inclination
        # Update measurement f based on inclination
        inclination_radians = inclination  # np.radians(inclination)
        for m in measurements:
            m.f = (
                mean.f
                + (m.h - mean.h) * np.cos(inclination_radians)
                + (m.z - mean.z) * np.sin(inclination_radians)
                + ((m.e) ** 2 - (mean.e) ** 2) / (2 * mean.f)
            )
        # calculate average inclination
        inclination = np.average(
            [
                (
                    m.measurement_type.shift
                    + m.measurement_type.meridian
                    * (
                        +m.angle
                        + m.measurement_type.direction
                        * (reading.hemisphere * np.degrees(np.arcsin(m.residual / m.f)))
                    )
                )
                for m in measurements
            ]
        )
    # calculate corrected f
    f = np.average([m.f for m in measurements]) + reading.pier_correction
    return inclination, f, mean


def calculate_HZ_absolutes(
    inclination: float, f: float, mean: AverageMeasurement, reference: Measurement
):
    inclination_radians = np.radians(inclination)
    h_abs = f * np.cos(inclination_radians)
    z_abs = f * np.sin(inclination_radians)
    h_b = round(np.sqrt(h_abs ** 2 - mean.e ** 2) - mean.h, 1)
    z_b = round(z_abs - mean.z, 1)
    # adjust absolutes to reference measurement
    h_abs = np.sqrt((h_b + reference.h) ** 2 + (reference.e) ** 2)
    z_abs = z_b + reference.z
    # return absolutes
    return (
        Absolute(
            element="H",
            baseline=h_b,
            absolute=h_abs,
            starttime=mean.time,
            endtime=mean.endtime,
        ),
        Absolute(
            element="Z",
            baseline=z_b,
            absolute=z_abs,
            starttime=mean.time,
            endtime=mean.endtime,
        ),
    )


def calculate_D_absolute(
    reading, absoluteH: Absolute, reference: Measurement
) -> Absolute:
    """
    Calculate declination absolute and declination baseline from
    ordinates, measurements, measurement_index(dictionary), azimuth and H baseline
    Returns absolute and baseline for declination.
    """
    index = measurement_index(reading.measurements)
    # mean across all declination measurements
    mean = reading.get_average(DECLINATION_TYPES)
    # average mark
    average_mark = reading.get_average(MARK_TYPES).angle
    # adjust based on which is larger
    mark_up = index[mt.FIRST_MARK_UP][0]
    mark_down = index[mt.FIRST_MARK_DOWN][0]
    if mark_up.angle < mark_down.angle:
        average_mark += 90
    else:
        average_mark -= 90
    # declination measurements
    measurements = [reading.get_average(t) for t in DECLINATION_TYPES]
    # average declination meridian
    h_base = absoluteH.baseline
    meridian = np.average(
        [
            (
                m.angle
                + np.degrees(
                    m.measurement_type.meridian
                    * (np.arcsin(m.residual / np.sqrt((m.h + h_base) ** 2 + m.e ** 2)))
                )
                - np.degrees(np.arctan(m.e / (m.h + h_base)))
            )
            for m in measurements
        ]
    )
    # add subtract average mark angle from average meridian angle and add
    # azimuth to get the declination baseline
    d_b = (meridian - average_mark) + reading.azimuth
    # calculate absolute
    d_abs = d_b + np.degrees(np.arctan(reference.e / (reference.h + h_base)))
    return Absolute(element="D", absolute=d_abs, baseline=d_b)


def calculate_scale(inclination: float, f: float, measurements: List[Measurement]):
    """
    Calculate scale value from calulated f(from inclination computations),
    inclination, and the measurements/ordinates taken for scaling purposes.
    Such measurements usually present themselves as a set of three North Down
    measurements, where the final two measuremets(and ordinates) are used for scaling.
    """
    inclination_radians = np.radians(inclination)
    scale0, scale1 = measurements[0], measurements[-1]
    field_change = (
        np.degrees(
            (
                -np.sin(inclination_radians) * (scale1.h - scale0.h)
                + np.cos(inclination_radians) * (scale1.z - scale0.z)
            )
            / f
        )
        + 0.1668
    )
    residual_change = scale1.residual - scale0.residual
    scale_value = f * field_change / np.abs(residual_change)
    return scale_value
