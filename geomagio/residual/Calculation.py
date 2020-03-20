import numpy as np
from .Ordinate import Ordinate


# class object for caclculations.
class Calculate(object):
    def __init__(
        self,
        angle: float = None,
        ordinate: Ordinate = None,
        inclination: float = None,
        f: float = None,
        meridian: float = None,
    ):
        self.angle = angle
        self.ordinate = ordinate
        self.inclination = inclination
        self.f = f
        self.meridian = meridian


def calculate_I(measurements, ordinates, ordinates_index, metadata):
    # average ordinates for all channels
    total_ordinate = average_ordinate(ordinates, None)
    # get first inclination angle, assumed to be southdown
    Iprime = average_angle(measurements, "SouthDown")
    if Iprime >= 90:
        Iprime -= 180
    Iprime = np.deg2rad(Iprime)
    # gather average angles for each measurement type
    southdown = process_type(
        Iprime, measurements, ordinates_index, total_ordinate, None, "SouthDown"
    )
    southup = process_type(
        Iprime, measurements, ordinates_index, total_ordinate, None, "SouthUp"
    )
    northdown = process_type(
        Iprime, measurements, ordinates_index, total_ordinate, None, "NorthDown"
    )
    northup = process_type(
        Iprime, measurements, ordinates_index, total_ordinate, None, "NorthUp"
    )
    # calculate average f that will take the place of f_mean in the next step
    fo = np.average([southdown.f, southup.f, northdown.f, northup.f])
    # get multiplier for hempisphere the observatory is located in
    hs = metadata["hemisphere"]
    # calculate f for every measurement type
    southdown.inclination = calculate_inclination(
        -180, southdown.angle, 1, southdown.residual, southdown.f, hs
    )
    northup.inclination = calculate_inclination(
        0, northup.angle, -1, northup.residual, northup.f, hs
    )
    southup.inclination = calculate_inclination(
        180, southup.angle, -1, southup.residual, southup.f, hs
    )
    northdown.inclination = calculate_inclination(
        0, northdown.angle, 1, northdown.residual, northdown.f, hs
    )
    # FIXME: Add looping to this method

    inclination = np.average(
        [
            southdown.inclination,
            northup.inclination,
            southup.inclination,
            northdown.inclination,
        ]
    )

    return inclination, fo, total_ordinate


def calculate_D(ordinates, measurements, measurements_index, AZ, Hb):
    # gather average angles for each measurement type
    westdown = process_type(None, measurements_index, ordinates, None, Hb, "WestDown")
    westup = process_type(None, measurements_index, ordinates, None, Hb, "WestUp")
    eastdown = process_type(None, measurements_index, ordinates, None, Hb, "EastDown")
    eastup = process_type(None, measurements_index, ordinates, None, Hb, "EastUp")
    # get average meridian angle from measurement types
    meridian = np.average(
        [westdown.meridian, westup.meridian, eastdown.meridian, eastup.meridian]
    )
    # compute average angle from marks
    average_mark = np.average(
        [m.angle for m in measurements if "mark" in m.measurement_type]
    )
    # add average mark, meridian, and azimuth angle to get declination baseline
    declination_baseline = average_mark + meridian + AZ

    return declination_baseline


def calculate_absolutes(f, I, pier_correction):

    i = np.deg2rad(I)
    Fabs = f + pier_correction
    Habs = Fabs * np.cos(i)
    Zabs = Fabs * np.sin(i)

    return Habs, Zabs, Fabs


def calculate_baselines(Habs, Zabs, total_ordinate):
    h_mean = total_ordinate.h
    e_mean = total_ordinate.e
    z_mean = total_ordinate.z

    Hb = np.sqrt(Habs ** 2 - e_mean ** 2) - h_mean
    Zb = Zabs - z_mean

    return Hb, Zb


def calculate_scale(f, measurements, I, pier_correction):
    i = np.deg2rad(I)
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
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        measurements = measurements[type][:-1]
    else:
        measurements = measurements[type]
    return np.average([m.angle for m in measurements])


def average_residual(measurements, type):
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        measurements = measurements[type][:-1]
    else:
        measurements = measurements[type]
    return np.average([m.residual for m in measurements])


def average_ordinate(ordinates, type):
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        ordinates = ordinates[type][:-1]
    elif type is not None:
        ordinates = ordinates[type]
    o = Ordinate(measurement_type=type)
    avgs = np.average([[o.h, o.e, o.z, o.f] for o in ordinates], axis=0,)
    o.h, o.e, o.z, o.f = avgs
    return o


def calculate_f(ordinate, total_ordinate, I):
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
        + (h - h_mean) * np.cos(I)
        + (z - z_mean) * np.sin(I)
        + ((e) ** 2 - (e_mean) ** 2) / (2 * f_mean)
    )
    return f


def calculate_inclination(shift, angle, ud, residual, f, hs):
    return shift + angle + ud * np.rad2deg(hs * np.sin(residual / f))


def process_type(I, measurements, ordinates, total_ordinate, baseline, type):
    c = Calculate()
    c.angle = average_angle(measurements, type)
    c.residual = average_residual(measurements, type)
    c.ordinate = average_ordinate(ordinates, type)
    if I is not None:
        c.f = calculate_f(c.ordinate, total_ordinate, I)
    elif baseline is not None:
        c.meridian = calculate_meridian_term(c, baseline)

    return c


def calculate_meridian_term(calculation, baseline):
    A1 = np.arcsin(
        calculation.residual
        / np.sqrt(
            (calculation.ordinate.h + baseline) ** 2 + (calculation.ordinate.e) ** 2
        )
    )
    A2 = np.arctan(calculation.ordinate.e / (calculation.ordinate.h + baseline))
    A1 = np.rad2deg(A1)
    A2 = np.rad2deg(A2)
    meridian_term = calculation.angle - A1 - A2
    return meridian_term
