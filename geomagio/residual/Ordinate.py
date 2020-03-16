from .MeasurementType import MeasurementType


class Ordinate(object):
    """One angle and time measurement with optional residual.

    Attributes
    ----------
    measurement_type: type of measurement.
    angle: measured angle, decimal degrees.
    residual: residual at time of measurement.
    time: when measurement was taken.
    ordinate: variometer data from time of measurement
    """

    def __init__(
        self,
        measurement_type: MeasurementType,
        h: float = 0,
        e: float = 0,
        z: float = 0,
        f: float = 0,
    ):
        self.measurement_type = measurement_type
        self.h = h
        self.e = e
        self.z = z
        self.f = f
