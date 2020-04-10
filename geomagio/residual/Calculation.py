import numpy as np
from .Ordinate import Ordinate
from .Absolute import Absolute
from .Angle import to_dms
from .MeasurementType import MeasurementType as mt
from pydantic import BaseModel


# specify mark measurement types
MARK_TYPES = [
    mt.FIRST_MARK_DOWN,
    mt.FIRST_MARK_UP,
    mt.SECOND_MARK_DOWN,
    mt.SECOND_MARK_UP,
]

# define measurement types used to calculate inclination
INCLINATION_TYPES = [mt.NORTH_DOWN, mt.NORTH_UP, mt.SOUTH_DOWN, mt.SOUTH_UP]


class Calculate(BaseModel):
    """
    Class object for performing calculations.
    Contains the following:
    angle: average angle across a measurement type
    residual: average residual across a measurement type
    hs: Multiplier for inclination claculations. +1 if measurment was taken in northern hemisphere, -1 if measurement was taken in the southern hemishpere.
    ordinate: Variometer data. Ordinate object(contains a datapoint for H, E, Z, and F)
    direction: Multiplier for inclination calculations. +1 if instrument is oriented upward, -1 if instrument if oriented downward.
    shift: Degree shift in inclination measurements.
    """

    angle: float = None
    residual: float = None
    ordinate: Ordinate = None
    f: float = None
    direction: int = None
    meridian: int = None
    shift: int = None


def calculate(reading):
    """
    Calculate/recalculate absolute from a Reading object's
    ordinates, measurements, and metadata.
    Outputs a list of absolutes containing baseline, absolute,
    and element name. Also reutrns the scale value.
    """
    # gather oridinates, measuremenets, and metadata objects from reading
    metadata = reading.metadata
    ordinates = reading.ordinates
    ordinate_index = reading.ordinate_index()
    measurements = reading.measurements
    measurement_index = reading.measurement_index()
    # get ordinate values across h, e, z, and f for inclination measurement types
    inclination_ordinates = [
        o for o in ordinates if o.measurement_type in INCLINATION_TYPES
    ]
    # get average ordinate values across h, e, z, and f
    mean = average_ordinate(inclination_ordinates, None)
    # calculate inclination
    inclination, f = calculate_I(
        measurement_index, inclination_ordinates, ordinate_index, mean, metadata,
    )
    # calculate absolutes
    h_abs, z_abs = calculate_absolutes(f, inclination)
    # calculate baselines for H and Z
    h_b, z_b = calculate_baselines(h_abs, z_abs, mean, reading.pier_correction)
    # calculate scale value
    scale_ordinates = ordinate_index[mt.NORTH_DOWN_SCALE]
    scale_measurements = measurement_index[mt.NORTH_DOWN_SCALE]
    scale = calculate_scale(f, scale_ordinates, scale_measurements, inclination,)
    # calculate declination absolute and baseline
    d_b, d_abs = calculate_D(
        ordinate_index, measurements, measurement_index, metadata["mark_azimuth"], h_b,
    )

    # return results as a set of Absolute objects along with the calculated scale value
    resultH = Absolute(element="H", baseline=h_b, absolute=h_abs)
    resultD = Absolute(element="D", baseline=d_b, absolute=d_abs)
    resultZ = Absolute(element="Z", baseline=z_b, absolute=z_abs)

    result = [resultH, resultD, resultZ]

    return result, scale


def calculate_I(measurements, ordinates, ordinates_index, mean, metadata):
    """
    Calculate inclination angles from measurements, ordinates,
    average ordinates from every measurement, and metadata.
    Returns inclination angle and calculated average f
    """
    # get first inclination angle, assumed to be the southdown angle
    Iprime = average_angle(measurements, mt.SOUTH_DOWN)
    if Iprime >= 100:
        Iprime -= 200
    # get multiplier for hempisphere the observatory is located in
    # 1 if observatory is in northern hemisphere
    # -1 if observatory is in southern hemisphere
    hs = metadata["hemisphere"]
    # gather calculation objects for each measurement type
    southdown = Calculate(
        shift=mt.SOUTH_DOWN.shift,
        direction=mt.SOUTH_DOWN.direction,
        meridian=mt.SOUTH_DOWN.meridian,
        angle=average_angle(measurements, mt.SOUTH_DOWN),
        residual=average_residual(measurements, mt.SOUTH_DOWN),
        ordinate=average_ordinate(ordinates_index, mt.SOUTH_DOWN),
    )

    southup = Calculate(
        shift=mt.SOUTH_UP.shift,
        direction=mt.SOUTH_UP.direction,
        meridian=mt.SOUTH_UP.meridian,
        angle=average_angle(measurements, mt.SOUTH_UP),
        residual=average_residual(measurements, mt.SOUTH_UP),
        ordinate=average_ordinate(ordinates_index, mt.SOUTH_UP),
    )

    northup = Calculate(
        shift=mt.NORTH_UP.shift,
        direction=mt.NORTH_UP.direction,
        meridian=mt.NORTH_UP.meridian,
        angle=average_angle(measurements, mt.NORTH_UP),
        residual=average_residual(measurements, mt.NORTH_UP),
        ordinate=average_ordinate(ordinates_index, mt.NORTH_UP),
    )

    northdown = Calculate(
        shift=mt.NORTH_DOWN.shift,
        direction=mt.NORTH_DOWN.direction,
        meridian=mt.NORTH_DOWN.meridian,
        angle=average_angle(measurements, mt.NORTH_DOWN),
        residual=average_residual(measurements, mt.NORTH_DOWN),
        ordinate=average_ordinate(ordinates_index, mt.NORTH_DOWN),
    )
    # set inclination value for looping = Iprime
    inclination = Iprime
    # add one to inclination value to enter the loop
    Inclination = inclination + 1
    # loop condition
    while abs(Inclination - inclination) > 0.0001:
        # set temporary inclination variable to hold previous step's inclination
        Inclination = inclination
        # calculate f for inclination measurement types
        southdown.f = calculate_f(southdown.ordinate, mean, inclination)
        northdown.f = calculate_f(northdown.ordinate, mean, inclination)
        southup.f = calculate_f(southup.ordinate, mean, inclination)
        northup.f = calculate_f(northup.ordinate, mean, inclination)
        # gather measurements into array(necessary because f were recalculated)
        measurements = [southup, southdown, northup, northdown]
        # average f values for inclination measurement types
        f = np.average([i.f for i in measurements])
        # calculation inclination for each inclination measurement type and average
        inclination = np.average(
            [calculate_measurement_inclination(m, hs) for m in measurements]
        )
    # loop exits once the difference in average inclination between steps is lower than 0.0001

    return inclination, f


def calculate_D(ordinates_index, measurements, measurements_index, azimuth, h_b):
    """
    Calculate declination absolute and declination baseline from
    ordinates, measurements, measurement_index(dictionary), azimuth and H baseline
    Returns absolute and baseline for declination.
    """

    # average mark angles
    # note that angles are being converted to geon
    average_mark = np.average(
        [
            convert_to_geon(m.angle)
            for m in measurements
            if m.measurement_type in MARK_TYPES
        ]
    )
    # add 100 if mark up is greater than mark down
    # subtract 100 otherwise
    if (
        measurements_index["FirstMarkUp"][0].angle
        < measurements_index["FirstMarkDown"][0].angle
    ):
        average_mark += 100
    else:
        average_mark -= 100

    # gather calculation objects for each declination measurement type
    # note that the meridian(plus minus) multiplier has been repurposed.
    # West facing measurements have a multiplier of -1
    # East facing measurements have a multipllier of 1
    westdown = Calculate(
        angle=average_angle(measurements_index, mt.WEST_DOWN),
        residual=average_residual(measurements_index, mt.WEST_DOWN),
        ordinate=average_ordinate(ordinates_index, mt.WEST_DOWN),
        meridian=mt.WEST_DOWN.meridian,
    )
    westup = Calculate(
        angle=average_angle(measurements_index, mt.WEST_UP),
        residual=average_residual(measurements_index, mt.WEST_UP),
        ordinate=average_ordinate(ordinates_index, mt.WEST_UP),
        meridian=mt.WEST_UP.meridian,
    )
    eastdown = Calculate(
        angle=average_angle(measurements_index, mt.EAST_DOWN),
        residual=average_residual(measurements_index, mt.EAST_DOWN),
        ordinate=average_ordinate(ordinates_index, mt.EAST_DOWN),
        meridian=mt.EAST_DOWN.meridian,
    )
    eastup = Calculate(
        angle=average_angle(measurements_index, mt.EAST_UP),
        residual=average_residual(measurements_index, mt.EAST_UP),
        ordinate=average_ordinate(ordinates_index, mt.EAST_UP),
        meridian=mt.EAST_UP.meridian,
    )
    # convert azimuth to geon
    azimuth = (int(azimuth / 100) + (azimuth % 100) / 60) / 0.9
    # gather declination measurements into array
    measurements = [westdown, westup, eastdown, eastup]
    # average meridian terms calculated from each declination measurements
    meridian = np.average([calculate_meridian_term(i, h_b) for i in measurements])
    # add subtract average mark angle from average meridian angle and add
    # azimuth(in geon) to get the declination baseline
    D_b = (meridian - average_mark) + azimuth
    # convert decimal baseline into dms baseline
    d_b = round(D_b * 54, 2)
    d_b_dms = int(d_b / 60) * 100 + ((d_b / 60) % 1) * 60
    # gather first declination measurements' H ans E ordinates
    wd_E_1 = ordinates_index[mt.WEST_DOWN][0].e
    wd_H_1 = ordinates_index[mt.WEST_DOWN][0].h
    # calculate Declination baseline
    d_abs = D_b + np.arctan(wd_E_1 / (h_b + wd_H_1)) * (200 / np.pi)
    d_abs = round(d_abs * 54, 1)
    # convert decimal absolute into dms absolute
    d_abs_dms = int(d_abs / 60) * 100 + ((d_abs / 60) % 1) * 60

    return d_b_dms, d_abs_dms


def calculate_absolutes(f, inclination):
    """
    Calculate absolutes for H, Z and F from computed
    average f value(from inclination computations) and
    calculated inclination angle.
    Returns baselines for H and Z
    """
    # convert inclination to radians
    i = (np.pi / 200) * (inclination)
    h_abs = f * np.cos(i)
    z_abs = f * np.sin(i)

    return h_abs, z_abs


def calculate_baselines(h_abs, z_abs, mean, pier_correction):
    """
    Calculate baselines with H and Z absolutes,
    average ordinates across all measurements,
    and pier correction(metadata).
    Returns H and Z baselines
    """
    correction = pier_correction / 5
    h_b = round(np.sqrt(h_abs ** 2 - mean.e ** 2) - mean.h, 1) - correction
    z_b = round(z_abs - mean.z, 1) - correction

    return h_b, z_b


def calculate_scale(f, ordinates, measurements, inclination):
    """
    Calculate scale value from calulated f(from inclination computations),
    inclination, and the measurements/ordinates taken for scaling purposes.
    Such measurements usually present themselves as a set of three North Down
    measurements, where the final two measuremets(and ordinates) are used for scaling.
    """
    first_ord = ordinates[0]
    second_ord = ordinates[1]
    first_measurement = measurements[0]
    second_measurement = measurements[1]

    field_change = (
        (
            -np.sin(inclination * np.pi / 200) * (second_ord.h - first_ord.h) / f
            + np.cos(inclination * np.pi / 200) * (second_ord.z - first_ord.z) / f
        )
        * 200
        / np.pi
    )

    field_change += 0.1852

    residual_change = abs(second_measurement.residual - first_measurement.residual)

    scale_value = (f * field_change / residual_change) * np.pi / 200

    return scale_value


def average_angle(measurements, type):
    """
    Compute average angle from a dictionary of
    measurements and specified measurement type.
    """
    return np.average([convert_to_geon(m.angle) for m in measurements[type]])


def average_residual(measurements, type):
    """
    Compute average residual from a dictionary
    of measurements and specified measurement type.
    """
    return np.average([m.residual for m in measurements[type]])


def average_ordinate(ordinates, type):
    """
    Compute average ordinate from a dictionary
    of ordinates and specified measurement type.
    """
    if type is not None:
        ordinates = ordinates[type]
    o = Ordinate(measurement_type=type)
    avgs = np.average([[o.h, o.e, o.z, o.f] for o in ordinates], axis=0,)
    o.h, o.e, o.z, o.f = avgs
    return o


def calculate_f(ordinate, mean, inclination):
    """
    calculate f for a measurement type using a measurement's
    average ordinates, average ordinate across all measurements,
    and calculated inclination.
    """
    # get channel means form all ordinates
    # calculate f using current step's inclination angle
    f = (
        mean.f
        + (ordinate.h - mean.h) * np.cos(inclination * np.pi / 200)
        + (ordinate.z - mean.z) * np.sin(inclination * np.pi / 200)
        + ((ordinate.e) ** 2 - (mean.e) ** 2) / (2 * mean.f)
    )
    return f


def calculate_measurement_inclination(calculation, hs):
    """
    Calculate a measurement's inclination value using
    Calculate items' elements.
    """
    return calculation.shift + calculation.meridian * (
        +calculation.angle
        + calculation.direction
        * (hs * np.arcsin(calculation.residual / calculation.f) * 200 / np.pi)
    )


def calculate_meridian_term(calculation, h_b):
    """
    Calculate meridian value from a measurement type
    using a Calculate object and H's baseline value.
    """
    A1 = np.arcsin(
        calculation.residual
        / np.sqrt((calculation.ordinate.h + h_b) ** 2 + (calculation.ordinate.e) ** 2)
    )
    A2 = np.arctan(calculation.ordinate.e / (calculation.ordinate.h + h_b))
    A1 = (200 / np.pi) * (A1)
    A2 = (200 / np.pi) * (A2)
    meridian_term = calculation.angle + (calculation.meridian * A1) - A2
    return meridian_term


def convert_to_geon(angle, incldirectione_seconds=True):
    """
    Convert angles from measurements to geon
    """
    degrees = int(angle)
    minutes = int((angle % 1) * 100) / 60
    if incldirectione_seconds:
        seconds = ((angle * 100) % 1) / 36
    else:
        seconds = 0
    dms = (degrees + minutes + seconds) / 0.9

    return dms
