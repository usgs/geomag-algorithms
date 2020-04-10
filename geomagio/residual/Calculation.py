import numpy as np
from .Ordinate import Ordinate
from .Absolute import Absolute
from .Angle import to_dms
from .MeasurementType import MeasurementType as mt
from pydantic import BaseModel


class Calculate(BaseModel):
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

    angle: float = None
    residual: float = None
    ordinate: Ordinate = None
    f: float = None
    ud: int = None
    pm: int = None
    shift: int = None


def calculate(Reading):
    """
    Calculate/recalculate absolute from a Reading object's
    ordinates, measurements, and metadata.
    Outputs a list of absolutes containing baseline, absolute,
    and element name. Also reutrns the scale value.
    """
    # define measurement types used to calculate inclination
    inclination_types = [mt.NORTH_DOWN, mt.NORTH_UP, mt.SOUTH_DOWN, mt.SOUTH_UP]
    # get ordinate values across h, e, z, and f for inclination measurement types
    inclination_ordinates = [
        o for o in Reading.ordinates if o.measurement_type in inclination_types
    ]
    # get average ordinate values across h, e, z, and f
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
    Habs, Zabs = calculate_absolutes(f, inclination)
    # calculate baselines for H and Z
    Hb, Zb = calculate_baselines(Habs, Zabs, mean, Reading.pier_correction)
    # calculate scale value
    scale_ordinates = Reading.ordinate_index()["NorthDownScale"]
    scale_measurements = Reading.measurement_index()["NorthDownScale"]
    scale = calculate_scale(f, scale_ordinates, scale_measurements, inclination,)
    # calculate declination absolute and baseline
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
    # get first inclination angle, assumed to be the southdown angle
    Iprime = average_angle(measurements, "SouthDown")
    if Iprime >= 100:
        Iprime -= 200
    # get multiplier for hempisphere the observatory is located in
    # 1 if observatory is in northern hemisphere
    # -1 if observatory is in southern hemisphere
    hs = metadata["hemisphere"]
    # gather calculation objects for each measurement type
    southdown = Calculate(
        shift=-200,
        ud=1,
        pm=1,
        angle=average_angle(measurements, "SouthDown"),
        residual=average_residual(measurements, "SouthDown"),
        ordinate=average_ordinate(ordinates_index, "SouthDown"),
    )

    southup = Calculate(
        shift=200,
        ud=-1,
        pm=-1,
        angle=average_angle(measurements, "SouthUp"),
        residual=average_residual(measurements, "SouthUp"),
        ordinate=average_ordinate(ordinates_index, "SouthUp"),
    )

    northup = Calculate(
        shift=0,
        ud=-1,
        pm=1,
        angle=average_angle(measurements, "NorthUp"),
        residual=average_residual(measurements, "NorthUp"),
        ordinate=average_ordinate(ordinates_index, "NorthUp"),
    )

    northdown = Calculate(
        shift=400,
        ud=1,
        pm=-1,
        angle=average_angle(measurements, "NorthDown"),
        residual=average_residual(measurements, "NorthDown"),
        ordinate=average_ordinate(ordinates_index, "NorthDown"),
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


def calculate_D(ordinates_index, measurements, measurements_index, AZ, Hb):
    """
    Calculate declination absolute and declination baseline from
    ordinates, measurements, measurement_index(dictionary), azimuth and H baseline
    Returns absolute and baseline for declination.
    """
    # specify mark measurement types
    mark_types = [
        mt.FIRST_MARK_DOWN,
        mt.FIRST_MARK_UP,
        mt.SECOND_MARK_DOWN,
        mt.SECOND_MARK_UP,
    ]
    # average mark angles
    # note that angles are being converted to geon
    average_mark = np.average(
        [
            convert_to_geon(m.angle)
            for m in measurements
            if m.measurement_type in mark_types
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
    # note that the pm(plus minus) multiplier has been repurposed.
    # West facing measurements have a multiplier of -1
    # East facing measurements have a multipllier of 1
    westdown = Calculate(
        angle=average_angle(measurements_index, "WestDown"),
        residual=average_residual(measurements_index, "WestDown"),
        ordinate=average_ordinate(ordinates_index, "WestDown"),
        pm=-1,
    )
    westup = Calculate(
        angle=average_angle(measurements_index, "WestUp"),
        residual=average_residual(measurements_index, "WestUp"),
        ordinate=average_ordinate(ordinates_index, "WestUp"),
        pm=-1,
    )
    eastdown = Calculate(
        angle=average_angle(measurements_index, "EastDown"),
        residual=average_residual(measurements_index, "EastDown"),
        ordinate=average_ordinate(ordinates_index, "EastDown"),
        pm=1,
    )
    eastup = Calculate(
        angle=average_angle(measurements_index, "EastUp"),
        residual=average_residual(measurements_index, "EastUp"),
        ordinate=average_ordinate(ordinates_index, "EastUp"),
        pm=1,
    )
    # convert azimuth to geon
    AZ = (int(AZ / 100) + (AZ % 100) / 60) / 0.9
    # gather declination measurements into array
    measurements = [westdown, westup, eastdown, eastup]
    # average meridian terms calculated from each declination measurements
    meridian = np.average([calculate_meridian_term(i, Hb) for i in measurements])
    # add subtract average mark angle from average meridian angle and add
    # azimuth(in geon) to get the declination baseline
    D_b = (meridian - average_mark) + AZ
    # convert decimal baseline into dms baseline
    Db = round(D_b * 54, 2)
    Db_dms = int(Db / 60) * 100 + ((Db / 60) % 1) * 60
    # gather first declination measurements' H ans E ordinates
    wd_E_1 = ordinates_index["WestDown"][0].e
    wd_H_1 = ordinates_index["WestDown"][0].h
    # calculate Declination baseline
    Dabs = D_b + np.arctan(wd_E_1 / (Hb + wd_H_1)) * (200 / np.pi)
    Dabs = round(Dabs * 54, 1)
    # convert decimal absolute into dms absolute
    Dabs_dms = int(Dabs / 60) * 100 + ((Dabs / 60) % 1) * 60

    return Db_dms, Dabs_dms


def calculate_absolutes(f, inclination):
    """
    Calculate absolutes for H, Z and F from computed
    average f value(from inclination computations) and
    calculated inclination angle.
    Returns baselines for H and Z
    """
    # convert inclination to radians
    i = (np.pi / 200) * (inclination)
    Habs = f * np.cos(i)
    Zabs = f * np.sin(i)

    return Habs, Zabs


def calculate_baselines(Habs, Zabs, mean, pier_correction):
    """
    Calculate baselines with H and Z absolutes,
    average ordinates across all measurements,
    and pier correction(metadata).
    Returns H and Z baselines
    """
    correction = pier_correction / 5
    Hb = round(np.sqrt(Habs ** 2 - mean.e ** 2) - mean.h, 1) - correction
    Zb = round(Zabs - mean.z, 1) - correction

    return Hb, Zb


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
    return calculation.shift + calculation.pm * (
        +calculation.angle
        + calculation.ud
        * (hs * np.arcsin(calculation.residual / calculation.f) * 200 / np.pi)
    )


def calculate_meridian_term(calculation, Hb):
    """
    Calculate meridian value from a measurement type
    using a Calculate object and H's baseline value.
    """
    A1 = np.arcsin(
        calculation.residual
        / np.sqrt((calculation.ordinate.h + Hb) ** 2 + (calculation.ordinate.e) ** 2)
    )
    A2 = np.arctan(calculation.ordinate.e / (calculation.ordinate.h + Hb))
    A1 = (200 / np.pi) * (A1)
    A2 = (200 / np.pi) * (A2)
    meridian_term = calculation.angle + (calculation.pm * A1) - A2
    return meridian_term


def convert_to_geon(angle, include_seconds=True):
    """
    Convert angles from measurements to geon
    """
    degrees = int(angle)
    minutes = int((angle % 1) * 100) / 60
    if include_seconds:
        seconds = ((angle * 100) % 1) / 36
    else:
        seconds = 0
    dms = (degrees + minutes + seconds) / 0.9

    return dms
