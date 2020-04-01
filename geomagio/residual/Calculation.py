import numpy as np
from .Ordinate import Ordinate
from .Absolute import Absolute


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
        hs: int = None,
        ud: int = None,
        shift: int = None,
    ):
        self.angle = angle
        self.residual = residual
        self.ordinate = ordinate
        self.baseline = baseline
        self.hs = hs
        self.ud = ud
        self.shift = shift


def calculate(Reading):
    # get average ordinate values across h, e, z, and f
    # FIXME: call this mean
    mean = average_ordinate(Reading.ordinates, None)
    # calculate inclination
    inclination, f = calculate_I(
        Reading.measurement_index(),
        Reading.ordinates,
        Reading.ordinate_index(),
        mean,
        Reading.metadata,
    )
    # calculate absolutes
    # FIXME: change to self.pier_correction
    Habs, Zabs, Fabs = calculate_absolutes(
        f, inclination, Reading.metadata["pier_correction"]
    )
    # calculate baselines
    Hb, Zb = calculate_baselines(Habs, Zabs, mean)
    # calculate scale value for declination
    scale_measurements = Reading.measurement_index()["NorthDownScale"]
    scale = calculate_scale(
        f, scale_measurements, inclination, Reading.metadata["pier_correction"]
    )
    # calculate declination and
    Db, Dabs = calculate_D(
        Reading.ordinates,
        Reading.measurements,
        Reading.measurement_index(),
        Reading.metadata["mark_azimuth"],
        Hb,
    )

    # return results as a set of Absolute objects along with the calculated scale value
    resultH = Absolute(element="H", baseline=Hb, absolute=Habs)
    resultD = Absolute(element="D", baseline=Db, absolute=Dabs)
    resultZ = Absolute(element="Z", baseline=Zb, absolute=Zabs)
    resultF = Absolute(element="F", baseline=None, absolute=Fabs)
    result = [resultH, resultD, resultZ, resultF]

    return result


def calculate_I(measurements, ordinates, ordinates_index, mean, metadata):
    """
    Calculate inclination angles from measurements, ordinates,
    average ordinates from every measurement, and metadata.
    Returns inclination angle and calculated average f
    """
    # get first inclination angle, assumed to be southdown
    Iprime = measurements["SouthDown"][0].angle
    if Iprime >= 90:
        Iprime -= 180
    Iprime = np.deg2rad(Iprime)
    print(Iprime)
    # get multiplier for hempisphere the observatory is located in
    # 1 if observatory is in northern hemisphere
    # -1 if observatory is in southern hemisphere
    hs = metadata["hemisphere"]
    # gather calculation objects for each measurement type
    # FIXME: create calculation objects inline

    # c = Calculate()
    # c.angle = average_angle(measurements, type)
    # c.residual = average_residual(measurements, type)
    # c.ordinate = average_ordinate(ordinates, type)
    # c.hs = hs
    # c.ud = ud
    # c.shift = shift
    # c.baseline = baseline

    southdown = Calculate(
        shift=-180,
        ud=-1,
        hs=hs,
        angle=average_angle(measurements, "SouthDown"),
        residual=average_residual(measurements, "SouthDown"),
        ordinate=average_ordinate(ordinates_index, "SouthDown"),
    )

    southup = Calculate(
        shift=180,
        ud=1,
        hs=hs,
        angle=average_angle(measurements, "SouthUp"),
        residual=average_residual(measurements, "SouthUp"),
        ordinate=average_ordinate(ordinates_index, "SouthUp"),
    )

    northup = Calculate(
        shift=0,
        ud=1,
        hs=hs,
        angle=average_angle(measurements, "NorthUp"),
        residual=average_residual(measurements, "NorthUp"),
        ordinate=average_ordinate(ordinates_index, "NorthUp"),
    )

    northdown = Calculate(
        shift=0,
        ud=-1,
        hs=hs,
        angle=average_angle(measurements, "NorthDown"),
        residual=average_residual(measurements, "NorthDown"),
        ordinate=average_ordinate(ordinates_index, "NorthDown"),
    )

    # gather measurements into array
    measurements = [southdown, southup, northdown, northup]
    # Get average inclination from measurments
    inclination = np.average(
        [calculate_measurement_inclination(i, mean.f) for i in measurements]
    )
    # iterate calculations until the difference in the resultant inclination angle is less than 0.0001
    # intialize inclination for current step to be outside threshold specified in condition
    Inclination = inclination + 1
    while abs(inclination - Inclination) >= 0.0001:
        # establish the inclination angle as the previously calculated average inclination angle
        Inclination = inclination
        # calculate average f component from each measurement
        f_avg = np.average([calculate_f(i, mean, Inclination) for i in ordinates])
        # update ordinate's f value as the average f component
        # used in next iterations f_avg calculation
        mean.f = f_avg
        # re-calculate inclination for measurement types
        inclination = np.average(
            [calculate_measurement_inclination(i, mean.f) for i in measurements]
        )
        # transfer inclination angle from degrees to radians
        inclination = np.deg2rad(inclination)

    return inclination, mean.f


def calculate_D(ordinates_index, measurements, measurements_index, AZ, Hb):
    """
    Calculate declination absolute and declination baseline from
    ordinates, measurements, measurement_index(dictionary), azimuth and H baseline
    Returns absolute and baseline for declination.
    """
    # compute average angle from marks
    average_mark = np.average(
        [m.angle for m in measurements if "mark" in m.measurement_type.capitalize()]
    )

    # gather calculation objects for each measurement type
    westdown = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "WestDown"),
        residual=average_residual(measurements_index, "WestDown"),
    )
    westup = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "WestUp"),
        residual=average_residual(measurements_index, "WestUp"),
    )
    eastdown = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "EastDown"),
        residual=average_residual(measurements_index, "EastDown"),
    )
    eastup = Calculate(
        baseline=Hb,
        angle=average_angle(measurements_index, "EastUp"),
        residual=average_residual(measurements_index, "EastUp"),
    )
    # gather measurements into array
    measurements = [westdown, westup, eastdown, eastup]
    # get average meridian angle from measurement types
    meridian = np.average([calculate_meridian_term(i) for i in measurements])
    # add average mark, meridian, and azimuth angle to get declination baseline
    Db = (average_mark + meridian + AZ) * 60
    # calculate declination absolute
    Dabs = Db + np.arctan(westdown.ordinate.e / (Hb + westdown.ordinate.h)) * (
        10800 / np.pi
    )

    return Db, Dabs


def calculate_absolutes(f, inclination, pier_correction):
    """
    Calculate absolutes for H, Z and F from computed
    average f value(from inclination computations),
    calculated inclination angle, and pier correction(metadata).
    Returns baselines for H, Z, and F
    """
    i = np.deg2rad(inclination)
    Fabs = f + pier_correction
    Habs = Fabs * np.cos(i)
    Zabs = Fabs * np.sin(i)

    return Habs, Zabs, Fabs


def calculate_baselines(Habs, Zabs, mean):
    """
    Calculate baselines with H and Z absolutes, and
    average ordinates across all measurements.
    Returns H and Z baselines
    """
    Hb = np.sqrt(Habs ** 2 - mean.e ** 2) - mean.h
    Zb = Zabs - mean.z

    return Hb, Zb


# FIXME: call in scaling measurements rather than all measurements
def calculate_scale(f, measurements, inclination, pier_correction):
    """
    Calculate scale value from calulated f(from inclination computations),
    calculated inclination, and pier correction(metadata)
    """
    i = np.deg2rad(inclination)
    angle_diff = np.diff([m.angle for m in measurements]) / f
    A = np.cos(i) * angle_diff
    B = np.sin(i) * angle_diff
    delta_f = np.rad2deg(A - B)
    detla_r = abs(np.diff([m.residual for m in measurements]))
    time_delta = np.diff([m.time for m in measurements])
    delta_b = delta_f + (time_delta / 60.0)
    # scale_value = f * np.deg2rad(delta_b / detla_r)
    scale_value = 1

    return scale_value


def average_angle(measurements, type):
    """
    Compute average angle from a dictionary of
    measurements and specified measurement type.
    """
    # FIXME: change repetitive checks
    return np.average([m.angle for m in measurements[type]])


def average_residual(measurements, type):
    """
    Compute average residual from a dictionary
    of measurements and specified measurement type.
    """
    # FIXME: change repetitive checks
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
        + (ordinate.h - mean.h) * np.cos(inclination)
        + (ordinate.z - mean.z) * np.sin(inclination)
        + ((mean.e) ** 2 - (mean.e) ** 2) / (2 * mean.f)
    )
    return f


def calculate_measurement_inclination(calc, f):
    """
    Calculate a measurement's inclination value using
    Calculate items' elements.
    """
    return (
        calc.shift
        + calc.angle
        + calc.ud * np.rad2deg(calc.hs * np.sin(calc.residual / f))
    )


def process_type(
    measurements,
    ordinates,
    type,
    mean=None,
    shift=None,
    ud=None,
    inclination=None,
    baseline=None,
    hs=None,
):
    """
    Create a Calculation object for each
    measurement within a measurement type.
    """
    c = Calculate()
    c.angle = average_angle(measurements, type)
    c.residual = average_residual(measurements, type)
    c.ordinate = average_ordinate(ordinates, type)
    c.hs = hs
    c.ud = ud
    c.shift = shift
    c.baseline = baseline

    return c


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
    A1 = np.rad2deg(A1)
    A2 = np.rad2deg(A2)
    meridian_term = calculation.angle - A1 - A2
    return meridian_term
