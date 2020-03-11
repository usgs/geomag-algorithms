import collections
from typing import Dict, List, Optional

from pydantic import BaseModel

from .Absolute import Absolute
from .Measurement import Measurement
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
    """

    absolutes: Optional[List[Absolute]] = None
    azimuth: float = 0
    hemisphere: float = 1  # maybe hemisphere should be calculated from latitude
    measurements: Optional[List[Measurement]] = []
    metadata: Optional[Dict] = []
    pier_correction: float = 0

    def absolutes_index(self) -> Dict[str, Absolute]:
        """Generate index of absolutes keyed by element.
        """
        return {a.element: a for a in self.absolutes}

<<<<<<< HEAD
    def calculate_absolutes(self) -> List[Absolute]:
        """Use measurements and metadata to (re)calculate absolutes.
        """
        raise NotImplementedError("TODO: implement this")
=======
    def calculate_absolutes(self, f, I, pier_correction):
        I = np.deg2rad(I)
        Fabs = f + pier_correction
        Habs = Fabs * np.cos(I)
        Zabs = Fabs * np.sin(I)

        return Fabs, Habs, Zabs

    def calculate_baselines(self, Habs, Zabs, h_mean, e_mean, z_mean):
        Hb = math.sqrt(Habs ** 2 - e_mean ** 2) - h_mean
        Zb = Zabs - z_mean

        return Hb, Zb

    def calculate_scale(self, f, last_two, time_delta):
        I = np.deg2rad(I)
        angle_diff = (last_two[1].angle - last_two[0].angle) / f
        Fabs = f + pier_correction
        A = np.cos(I) * angle_diff[0]
        B = np.sin(I) * angle_diff[-1]
        delta_f = np.rad2deg(B - A)
        delta_r = abs(last_two[1].residual - last_two[0].residual)
        delta_b = delta_f + time_delta
        scale_value = f * np.deg2rad(delta_b / delta_r)

        return scale_value

    def calculate_I(self) -> List[Absolute]:
        """Use measurements and metadata to calculate inclination.
        """
        # constant inclination types
        I_TYPES = ["SouthDown", "Northdown", "SouthUp", "Northup"]
        # constant I calculations
        # calculate mean f from h, e, and z means and total ordinate means
        calculate_f = (
            lambda h, e, z: f_mean
            + (h - h_mean) * np.cos(IPrime)
            + (z - z_mean) * np.sin(IPrime)
            + ((e) ** 2 - (e_mean) ** 2) / (2 * f_mean)
        )
        # derived inclination angle from each measurement
        # shift: depends on measurement type
        # A: angle
        # ud: multiplier depending on whether or not theodolite is right-side up
        # R: average residual for measurement type
        # F: derived f for measurement type
        calc_I = (
            lambda shift, A, ud, R, F: shift
            + A
            + ud * np.rad2deg(metadata["hemisphere"] * np.sin(R / F))
        )

        # set first calculation's I angle to the average Southdown angle
        # flip I angle if Southdown was 90 degrees or greater
        IPrime = ang_avg("SouthDown")
        if IPrime >= 90:
            IPrime -= 180
        # residual calculations are done in radians as specified by the paper
        IPrime = np.deg2rad(IPrime)
        # gather individual measurements' average ordinates
        ord_avs = [ord_avg(i) for i in I_TYPES]
        # gather all h, e, and z ordinate means from all inclination measurements
        h_mean, e_mean, z_mean, f_mean = np.average(ord_avs, axis=1)
        # calculate f for every inclination measurement type
        f_NU = calculate_f(ord_avg("NorthUp")[:-1])
        f_SD = calculate_f(ord_avg("SouthDown")[:-1])
        f_ND = calculate_f(ord_avg("NorthDown")[:-1])
        f_SU = calculate_f(ord_avg("SouthUp")[:-1])
        # average each measurement type's claculated f
        fmean = (f_NU + f_SD + f_ND + f_SU) / 4
        # calculate inclination angles for each measurement
        SD_I = calc_I(-180, ang_avg("SouthDown"), 1, res_avg("SouthDown"), f_SD)
        NU_I = calc_I(0, ang_avg("NorthUp"), -1, res_avg("NorthUp"), f_NU)
        SU_I = calc_I(180, ang_avg("SouthUp"), -1, res_avg("SouthUp"), f_SU)
        ND_I = calc_I(0, ang_avg("NorthDown"), 1, res_avg("NorthDown"), f_ND)
        # average each measurement's inclination angle
        I = np.average(SD_I, NU_I, SU_I, ND_I)
        # FIXME: NEED TO BUILD IN ITERATIONS

        return I
>>>>>>> remove WIP declination calculation, add calculate baseline method

    def measurement_index(self) -> Dict[MeasurementType, List[Measurement]]:
        """Generate index of measurements keyed by MeasurementType.

        Any missing MeasurementType returns an empty list.
        There may be multiple measurements of each MeasurementType.
        """
        index = collections.defaultdict(list)
        for m in self.measurements:
            index[m.measurement_type].append(m)
        return index
