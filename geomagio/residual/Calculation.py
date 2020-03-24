import numpy as np
from .Ordinate import Ordinate


# class object for performing calculations
class Calculate(object):
    def __init__(
        self,
        angle: float = None,
        residual: float = None,
        ordinate: Ordinate = None,
        hs: int = None,
        ud: int = None,
        shift: int = None,
    ):
        self.angle = angle
        self.residual = residual
        self.ordinate = ordinate
        self.hs = hs
        self.shift = shift


def calculate_I(measurements, ordinates, ordinates_index, total_ordinate, metadata):
    """
    Calculate inclination angles from measurements, ordinates,
    average ordinates from every measurement, and metadata.
    Returns inclination angle and calculated average f
    """
    # get first inclination angle, assumed to be southdown
    Iprime = average_angle(measurements, "SouthDown")
    if Iprime >= 90:
        Iprime -= 180
    Iprime = np.deg2rad(Iprime)
    # get multiplier for hempisphere the observatory is located in
    # 1 if observatory is in northern hemisphere
    # -1 if observatory is in southern hemisphere
    hs = metadata["hemisphere"]
    # gather average angles for each measurement type
    southdown = process_type(
        shift=-180,
        inclination=Iprime,
        ud=-1,
        measurements=measurements,
        ordinates=ordinates_index,
        total_ordinate=total_ordinate,
        type="SouthDown",
        hs=hs,
    )
    southup = process_type(
        shift=180,
        inclination=Iprime,
        ud=1,
        measurements=measurements,
        ordinates=ordinates_index,
        total_ordinate=total_ordinate,
        type="SouthUp",
        hs=hs,
    )
    northup = process_type(
        shift=0,
        inclination=Iprime,
        ud=1,
        measurements=measurements,
        ordinates=ordinates_index,
        total_ordinate=total_ordinate,
        type="NorthUp",
        hs=hs,
    )
    northdown = process_type(
        shift=0,
        inclination=Iprime,
        ud=-1,
        measurements=measurements,
        ordinates=ordinates_index,
        total_ordinate=total_ordinate,
        type="NorthDown",
        hs=hs,
    )
    # gather measurements into array
    measurements = [southdown, southup, northdown, northup]
    # Get average inclination from measurments
    inclination = np.average(
        [calculate_measurement_inclination(i, total_ordinate.f) for i in measurements]
    )
    # iterate calculations until the difference in the resultant inclination angle is less than 0.0001
    # intialize inclination for current step to be outside threshold specified in condition
    Inclination = inclination + 1
    while abs(inclination - Inclination) >= 0.0001:
        # establish the inclination angle as the previously calculated average inclination angle
        Inclination = inclination
        # calculate average f component from each measurement
        f_avg = np.average(
            [calculate_f(i, total_ordinate, Inclination) for i in ordinates]
        )
        # update ordinate's f value as the average f component
        # used in next iterations f_avg calculation
        total_ordinate.f = f_avg
        # re-calculate inclination for measurement types
        inclination = np.average(
            [
                calculate_measurement_inclination(i, total_ordinate.f)
                for i in measurements
            ]
        )
        # transfer inclination angle from degrees to radians
        inclination = np.deg2rad(inclination)

    return Inclination, total_ordinate.f


def calculate_D(ordinates, measurements, measurements_index, AZ, Hb):
    """
    Calculate declination absolute and declination baseline from
    ordinates, measurements, measurement_index(dictionary), azimuth and H baseline
    Returns absolute and baseline for declination.
    """
    # compute average angle from marks
    average_mark = np.average(
        [m.angle for m in measurements if "mark" in m.measurement_type.capitalize()]
    )
    # gather average angles for each measurement type
    southdown = process_type(
        measurements=measurements_index,
        ordinates=ordinates,
        baseline=Hb,
        type="SouthDown",
    )
    southup = process_type(
        measurements=measurements_index,
        ordinates=ordinates,
        baseline=Hb,
        type="SouthUp",
    )
    northdown = process_type(
        measurements=measurements_index,
        ordinates=ordinates,
        baseline=Hb,
        type="NorthDown",
    )
    northup = process_type(
        measurements=measurements_index,
        ordinates=ordinates,
        baseline=Hb,
        type="NorthUp",
    )
    # gather measurements into array
    measurements = [southdown, southup, northup, northdown]
    # get average meridian angle from measurement types
    meridian = np.average([calculate_meridian_term(i) for i in measurements])
    # add average mark, meridian, and azimuth angle to get declination baseline
    Db = (average_mark + meridian + AZ) * 60
    # calculate declination absolute
    Dabs = Db + np.arctan(southdown.ordinate.e / (Hb + southdown.ordinate.h)) * (
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


def calculate_baselines(Habs, Zabs, total_ordinate):
    """
    Calculate baselines with H and Z absolutes, and
    average ordinates across all measurements.
    Returns H and Z baselines
    """
    h_mean = total_ordinate.h
    e_mean = total_ordinate.e
    z_mean = total_ordinate.z

    Hb = np.sqrt(Habs ** 2 - e_mean ** 2) - h_mean
    Zb = Zabs - z_mean

    return Hb, Zb


def calculate_scale(f, measurements, inclination, pier_correction):
    """
    Calculate scale value from calulated f(from inclination computations),
    calculated inclination, and pier correction(metadata)
    """
    i = np.deg2rad(inclination)
    measurements = measurements[-2:]
    angle_diff = (np.diff([m.angle for m in measurements]) / f)[0]
    A = np.cos(i) * angle_diff
    B = np.sin(i) * angle_diff
    delta_f = np.rad2deg(A - B)
    detla_r = abs(np.diff([m.residual for m in measurements]))[0]
    time_delta = np.diff([m.time for m in measurements])[0]
    delta_b = delta_f + (time_delta / 60.0)
    scale_value = f * np.deg2rad(delta_b / detla_r)

    return scale_value


def average_angle(measurements, type):
    """
    Compute average angle from a dictionary of
    measurements and specified measurement type.
    """
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        measurements = measurements[type][:-1]
    else:
        measurements = measurements[type]
    return np.average([m.angle for m in measurements])


def average_residual(measurements, type):
    """
    Compute average residual from a dictionary
    of measurements and specified measurement type.
    """
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        measurements = measurements[type][:-1]
    else:
        measurements = measurements[type]
    return np.average([m.residual for m in measurements])


def average_ordinate(ordinates, type):
    """
    Compute average ordinate from a dictionary
    of ordinates and specified measurement type.
    """
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        ordinates = ordinates[type][:-1]
    elif type is not None:
        ordinates = ordinates[type]
    o = Ordinate(measurement_type=type)
    avgs = np.average([[o.h, o.e, o.z, o.f] for o in ordinates], axis=0,)
    o.h, o.e, o.z, o.f = avgs
    return o


def calculate_f(ordinate, total_ordinate, inclination):
    """
    calculate f for a measurement type using a measurement's
    average ordinates, average ordinate across all measurements,
    and calculated inclination.
    """
    # get channel means form all ordinates
    h_mean = total_ordinate.h
    e_mean = total_ordinate.e
    z_mean = total_ordinate.z
    f_mean = total_ordinate.f
    # get individual ordinate means
    h = ordinate.h
    e = ordinate.e
    z = ordinate.z
    # calculate f using current step's inclination angle
    f = (
        f_mean
        + (h - h_mean) * np.cos(inclination)
        + (z - z_mean) * np.sin(inclination)
        + ((e) ** 2 - (e_mean) ** 2) / (2 * f_mean)
    )
    return f


def calculate_measurement_inclination(calculation, f):
    """
    Calculate a measurement's inclination value using
    Calculate items' elements.
    """
    shift = calculation.shift
    angle = calculation.angle
    ud = calculation.ud
    hs = calculation.hs
    r = calculation.residual
    return shift + angle + ud * np.rad2deg(hs * np.sin(r / f))


def process_type(
    measurements,
    ordinates,
    type,
    total_ordinate=None,
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
