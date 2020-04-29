from typing import List, Tuple
from typing_extensions import Literal

import numpy as np
from pydantic import BaseModel

from .Absolute import Absolute
from .Angle import from_dms, to_dms
from .MeasurementType import (
    MeasurementType as mt,
    DECLINATION_TYPES,
    INCLINATION_TYPES,
    MARK_TYPES,
)
from .Measurement import (
    AverageMeasurement,
    Measurement,
    average_measurement,
    measurement_index,
)
from .Reading import Reading


def calculate(reading: Reading) -> Reading:
    """Calculate absolutes and scale value using residual method.

    Parameters
    -------
    reading: reading to calculate absolutes from.

    Returns
    -------
    new reading object with calculated absolutes and scale_value.
    NOTE: rest of reading object is shallow copy.
    """
    # reference measurement, used to adjust absolutes
    reference = reading[mt.WEST_DOWN][0]
    # calculate inclination
    inclination, f, mean = calculate_I(
        hemisphere=reading.hemisphere, measurements=reading.measurements
    )
    corrected_f = f + reading.pier_correction  # TODO: should this be returned?
    # calculate absolutes
    absoluteH, absoluteZ = calculate_HZ_absolutes(
        corrected_f=corrected_f, inclination=inclination, mean=mean, reference=reference
    )
    absoluteD = calculate_D_absolute(
        azimuth=reading.azimuth,
        h_baseline=absoluteH.baseline,
        measurements=reading.measurements,
        reference=reference,
    )
    # calculate scale
    scale_value = calculate_scale_value(
        corrected_f=corrected_f,
        inclination=inclination,
        measurements=reading[mt.NORTH_DOWN_SCALE],
    )
    # create new reading object
    calculated = Reading(
        absolutes=[absoluteD, absoluteH, absoluteZ],
        scale_value=scale_value,
        # copy other attributes
        **reading.dict(exclude={"absolutes", "scale_value"}),
    )
    return calculated


def calculate_D_absolute(
    measurements: List[Measurement],
    azimuth: float,
    h_baseline: float,
    reference: Measurement,
) -> Absolute:
    """Calculate D absolute.

    Parameters
    ----------
    measurements: list with at least declination and mark measurements.
    azimuth: azimuth to mark in decimal degrees.
    h_baseline: calculated H baseline value.
    reference: reference measurement used to adjust absolute.

    Returns
    -------
    D Absolute
    """
    # mean across all declination measurements
    mean = average_measurement(measurements, DECLINATION_TYPES)
    # average mark
    average_mark = average_measurement(measurements, MARK_TYPES).angle
    # adjust based on which is larger
    mark_up = average_measurement(measurements, [mt.FIRST_MARK_UP]).angle
    mark_down = average_measurement(measurements, [mt.FIRST_MARK_DOWN]).angle
    if mark_up < mark_down:
        average_mark += 90
    else:
        average_mark -= 90
    # declination measurements
    declination_measurements = [
        average_measurement(measurements, [t]) for t in DECLINATION_TYPES
    ]
    # average declination meridian
    meridian = np.average(
        [
            m.angle
            + np.degrees(
                m.measurement_type.meridian
                * (np.arcsin(m.residual / np.sqrt((m.h + h_baseline) ** 2 + m.e ** 2)))
            )
            - np.degrees(np.arctan(m.e / (m.h + h_baseline)))
            for m in declination_measurements
        ]
    )
    # add subtract average mark angle from average meridian angle and add
    # azimuth to get the declination baseline
    d_b = (meridian - average_mark) + azimuth
    # calculate absolute
    d_abs = d_b + np.degrees(np.arctan(reference.e / (reference.h + h_baseline)))
    return Absolute(element="D", absolute=d_abs, baseline=d_b)


def calculate_HZ_absolutes(
    inclination: float,
    corrected_f: float,
    mean: AverageMeasurement,
    reference: Measurement,
) -> Tuple[Absolute, Absolute]:
    """Calculate H and Z absolutes.

    Parameters
    ----------
    inclination: calculated inclination.
    corrected_f: calculated f with pier correction.
    mean: mean of inclination ordinates.
    reference:  reference measurement used to adjust absolutes.

    Returns
    -------
    Tuple
        - H Absolute
        - Z Absolute
    """
    inclination_radians = np.radians(inclination)
    h_abs = corrected_f * np.cos(inclination_radians)
    z_abs = corrected_f * np.sin(inclination_radians)
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


def calculate_I(
    measurements: List[Measurement], hemisphere: Literal[-1, 1] = 1
) -> Tuple[float, float, Measurement]:
    """Calculate inclination and f from measurements.

    Parameters
    ----------
    measurements: list with at least inclination measurements.
    hemisphere: +1 for northern hemisphere (default), -1 for southern hemisphere.

    Returns
    -------
    Tuple
        - inclination angle in decimal degrees
        - uncorrected calculated f
        - mean of inclination measurements
    """
    # mean across all inclination measurements
    mean = average_measurement(measurements, INCLINATION_TYPES)
    # mean within each type
    inclination_measurements = [
        average_measurement(measurements, [t]) for t in INCLINATION_TYPES
    ]
    # get initial inclination angle, assumed to be the southdown angle
    inclination = average_measurement(measurements, [mt.NORTH_DOWN]).angle
    if inclination >= 90:
        inclination -= 180
    # loop until inclination converges
    last_inclination = inclination + 1
    while abs(last_inclination - inclination) > 0.0001:
        # set temporary inclination variable to hold previous step's inclination
        last_inclination = inclination
        # Update measurement f based on inclination
        inclination_radians = np.radians(inclination)
        for m in inclination_measurements:
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
                        * (hemisphere * np.degrees(np.arcsin(m.residual / m.f)))
                    )
                )
                for m in inclination_measurements
            ]
        )
    # calculate uncorrected f
    f = np.average([m.f for m in inclination_measurements])
    return inclination, f, mean


def calculate_scale_value(
    measurements: List[Measurement], inclination: float, corrected_f: float
) -> float:
    """Calculate scale value.

    Parameters
    ----------
    measurements: measurements to be used for scale calculation.
        should have type NORTH_DOWN_SCALE.
    inclination: calculated inclination.
    corrected_f: calculated f with pier correction.

    Returns
    -------
    Calculated scale value.
    """
    inclination_radians = np.radians(inclination)
    m1, m2 = measurements[0], measurements[-1]
    field_change = (
        np.degrees(
            (
                -np.sin(inclination_radians) * (m2.h - m1.h)
                + np.cos(inclination_radians) * (m2.z - m1.z)
            )
            / corrected_f
        )
        + 0.1668
    )
    residual_change = m2.residual - m1.residual
    scale_value = corrected_f * field_change / np.abs(residual_change)
    return scale_value
