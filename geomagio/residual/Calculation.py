import numpy as np
from .Ordinate import Ordinate
from .Absolute import Absolute
from .Angle import to_dms
from .MeasurementType import MeasurementType as mt


class Calculate(object):
    """
    Class object for performing calculations.
    Contains the following:
    angle: average angle across a measurement type
    residual: average residual across a measurement type
    hs: Multiplier for inclination claculations. +1 if measurment was taken in northern hemisphere, -1 if measurement was taken in the southern hemishpere.
    ordinate: Variometer data. Ordinate object(contains a datapoint for H, E, Z, and F)
    ud: Multiplier for inclination calculations. +1 if instrument is oriented upward, -1 if instrument if oriented downward.
    shift: Degree shift in inclination measurements.
    """

    def __init__(
        self,
        angle: float = None,
        residual: float = None,
        ordinate: Ordinate = None,
        baseline: float = None,
        f: float = None,
        inclination: float = None,
        hs: int = None,
        ud: int = None,
        shift: int = None,
        pm: int = None,
    ):
        self.angle = angle
        self.residual = residual
        self.ordinate = ordinate
        self.baseline = baseline
        self.f = f
        self.inclination = inclination
        self.hs = hs
        self.ud = ud
        self.shift = shift
        self.pm = pm


def calculate(Reading):
    # get average ordinate values across h, e, z, and f
    inclination_ordinates = [
        o
        for o in Reading.ordinates
        if "West" not in o.measurement_type.capitalize()
        and "East" not in o.measurement_type.capitalize()
        and "NorthDownScale" not in o.measurement_type.capitalize()
    ]

    inclination_ordinates = inclination_ordinates[0:-2]
    mean = average_ordinate(inclination_ordinates, None)
    # calculate inclination
    inclination, f = calculate_I(
        Reading.measurement_index(),
        inclination_ordinates,
        Reading.ordinate_index(),
        mean,
        Reading.metadata,
    )
    # calculate absolutes
    # FIXME: change to self.pier_correction
    Habs, Zabs = calculate_absolutes(
        f, inclination, Reading.metadata["pier_correction"]
    )
    # calculate baselines
    Hb, Zb = calculate_baselines(Habs, Zabs, mean, Reading.pier_correction)
    # calculate scale value for declination
    scale_ordinates = Reading.ordinate_index()["NorthDownScale"]
    scale_measurements = Reading.measurement_index()["NorthDownScale"]
    scale = calculate_scale(
        f,
        scale_ordinates,
        scale_measurements,
        inclination,
        Reading.metadata["pier_correction"],
    )
    # calculate declination and
    Db, Dabs = calculate_D(
        Reading.ordinate_index(),
        Reading.measurements,
        Reading.measurement_index(),
        Reading.metadata["mark_azimuth"],
        Hb,
    )

    # return results as a set of Absolute objects along with the calculated scale value
    resultH = Absolute(element="H", baseline=Hb, absolute=Habs)
    resultD = Absolute(element="D", baseline=Db, absolute=Dabs)
    resultZ = Absolute(element="Z", baseline=Zb, absolute=Zabs)

    result = [resultH, resultD, resultZ]

    return result, scale


def calculate_I(measurements, ordinates, ordinates_index, mean, metadata):
    """
    Calculate inclination angles from measurements, ordinates,
    average ordinates from every measurement, and metadata.
    Returns inclination angle and calculated average f
    """
    # get first inclination angle, assumed to be southdown
    Iprime = average_angle(measurements, "SouthDown")
    if Iprime >= 100:
        Iprime -= 200
    # Iprime = (np.pi / 200)*(Iprime)
    # get multiplier for hempisphere the observatory is located in
    # 1 if observatory is in northern hemisphere
    # -1 if observatory is in southern hemisphere
    hs = metadata["hemisphere"]
    # gather calculation objects for each measurement type
    southdown = Calculate(
        shift=-200,
        ud=1,
        hs=hs,
        pm=1,
        angle=average_angle(measurements, "SouthDown"),
        residual=average_residual(measurements, "SouthDown"),
        ordinate=average_ordinate(ordinates_index, "SouthDown"),
    )

    southup = Calculate(
        shift=200,
        ud=-1,
        hs=hs,
        pm=-1,
        angle=average_angle(measurements, "SouthUp"),
        residual=average_residual(measurements, "SouthUp"),
        ordinate=average_ordinate(ordinates_index, "SouthUp"),
    )

    northup = Calculate(
        shift=0,
        ud=-1,
        hs=hs,
        pm=1,
        angle=average_angle(measurements, "NorthUp"),
        residual=average_residual(measurements, "NorthUp"),
        ordinate=average_ordinate(ordinates_index, "NorthUp"),
    )

    northdown = Calculate(
        shift=400,
        ud=1,
        hs=hs,
        pm=-1,
        angle=average_angle(measurements, "NorthDown"),
        residual=average_residual(measurements, "NorthDown"),
        ordinate=average_ordinate(ordinates_index, "NorthDown"),
    )

    inclination = Iprime
    Inclination = inclination + 1

    while abs(Inclination - inclination) > 0.0001:
        Inclination = inclination

        southdown.f = calculate_f(southdown.ordinate, mean, inclination)
        northdown.f = calculate_f(northdown.ordinate, mean, inclination)
        southup.f = calculate_f(southup.ordinate, mean, inclination)
        northup.f = calculate_f(northup.ordinate, mean, inclination)

        northup.inclination = calculate_measurement_inclination(northup)
        southdown.inclination = calculate_measurement_inclination(southdown)
        northdown.inclination = calculate_measurement_inclination(northdown)
        southup.inclination = calculate_measurement_inclination(southup)

        measurements = [southup, southdown, northup, northdown]

        inclination = np.average([i.inclination for i in measurements])
        f = np.average([i.f for i in measurements])

    return inclination, f


def calculate_D(ordinates_index, measurements, measurements_index, AZ, Hb):
    """
    Calculate declination absolute and declination baseline from
    ordinates, measurements, measurement_index(dictionary), azimuth and H baseline
    Returns absolute and baseline for declination.
    """
    # compute average angle from marks
    average_mark = np.average(
        [
            convert_to_geon(m.angle)
            for m in measurements
            if "mark" in m.measurement_type.capitalize()
        ]
    )

    if (
        measurements_index["FirstMarkUp"][0].angle
        < measurements_index["FirstMarkDown"][0].angle
    ):
        average_mark += 100
    else:
        average_mark -= 100

    # if average_mark < 200:
    #     average_mark += 100
    # else:
    #     average_mark -= 100

    # gather calculation objects for each measurement type
    westdown = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "WestDown"),
        residual=average_residual(measurements_index, "WestDown"),
        ordinate=average_ordinate(ordinates_index, "WestDown"),
        ud=-1,
    )
    westup = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "WestUp"),
        residual=average_residual(measurements_index, "WestUp"),
        ordinate=average_ordinate(ordinates_index, "WestUp"),
        ud=-1,
    )
    eastdown = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "EastDown"),
        residual=average_residual(measurements_index, "EastDown"),
        ordinate=average_ordinate(ordinates_index, "EastDown"),
        ud=1,
    )
    eastup = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "EastUp"),
        residual=average_residual(measurements_index, "EastUp"),
        ordinate=average_ordinate(ordinates_index, "EastUp"),
        ud=1,
    )
    # AZ = convert_to_geon(AZ, include_seconds=False)
    AZ = (int(AZ / 100) + (AZ % 100) / 60) / 0.9
    # gather measurements into array
    measurements = [westdown, westup, eastdown, eastup]
    # get average meridian angle from measurement types
    meridian = np.average([calculate_meridian_term(i) for i in measurements])
    # add average mark, meridian, and azimuth angle to get declination baseline
    Db_abs = (meridian - average_mark) + AZ
    Db = round(Db_abs * 54, 2)
    Db_dms = int(Db / 60) * 100 + ((Db / 60) % 1) * 60
    # calculate declination absolute
    wd_E_1 = ordinates_index["WestDown"][0].e
    wd_H_1 = ordinates_index["WestDown"][0].h
    Dabs = Db_abs + np.arctan(wd_E_1 / (Hb + wd_H_1)) * (200 / np.pi)
    Dabs = round(Dabs * 54, 1)
    Dabs_dms = int(Dabs / 60) * 100 + ((Dabs / 60) % 1) * 60

    return Db_dms, Dabs_dms


def calculate_absolutes(f, inclination, pier_correction):
    """
    Calculate absolutes for H, Z and F from computed
    average f value(from inclination computations),
    calculated inclination angle, and pier correction(metadata).
    Returns baselines for H, Z, and F
    """
    i = (np.pi / 200) * (inclination)
    Habs = f * np.cos(i)
    Zabs = f * np.sin(i)

    return Habs, Zabs


def calculate_baselines(Habs, Zabs, mean, pier_correction):
    """
    Calculate baselines with H and Z absolutes, and
    average ordinates across all measurements.
    Returns H and Z baselines
    """
    # FIXME: Figure out where 0.3 comes from
    correction = pier_correction / 5
    Hb = round(np.sqrt(Habs ** 2 - mean.e ** 2) - mean.h, 1) - correction
    Zb = round(Zabs - mean.z, 1) - correction

    return Hb, Zb


def calculate_scale(f, ordinates, measurements, inclination, pier_correction):
    """
    Calculate scale value from calulated f(from inclination computations),
    calculated inclination, and pier correction(metadata)
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
    # FIXME: change repetitive checks
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
    # FIXME: change repetitive checks
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
    # FIXME: don't unpack ordinates
    # calculate f using current step's inclination angle
    f = (
        mean.f
        + (ordinate.h - mean.h) * np.cos(inclination * np.pi / 200)
        + (ordinate.z - mean.z) * np.sin(inclination * np.pi / 200)
        + ((ordinate.e) ** 2 - (mean.e) ** 2) / (2 * mean.f)
    )
    return f


def calculate_measurement_inclination(calc):
    """
    Calculate a measurement's inclination value using
    Calculate items' elements.
    """
    return calc.shift + calc.pm * (
        +calc.angle
        + calc.ud * (calc.hs * np.arcsin(calc.residual / calc.f) * 200 / np.pi)
    )


def calculate_meridian_term(calculation):
    """
    Calculate meridian value from a measurement type
    using a Calculate object and H's baseline value.
    """
    A1 = np.arcsin(
        calculation.residual
        / np.sqrt(
            (calculation.ordinate.h + calculation.baseline) ** 2
            + (calculation.ordinate.e) ** 2
        )
    )
    A2 = np.arctan(
        calculation.ordinate.e / (calculation.ordinate.h + calculation.baseline)
    )
    A1 = (200 / np.pi) * (A1)
    A2 = (200 / np.pi) * (A2)
    meridian_term = calculation.angle + (calculation.ud * A1) - A2
    return meridian_term


def convert_to_geon(angle, include_seconds=True):
    degrees = int(angle)
    minutes = int((angle % 1) * 100) / 60
    if include_seconds:
        seconds = ((angle * 100) % 1) / 36
    else:
        seconds = 0
    dms = (degrees + minutes + seconds) / 0.9
    return dms
