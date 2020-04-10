import enum

# FIXME: add another measurement type that is a scaling measurement type
class MeasurementType(str, enum.Enum):
    """Measurement types used during absolutes."""

    # declination
    FIRST_MARK_UP = "FirstMarkUp"
    FIRST_MARK_DOWN = "FirstMarkDown"
    WEST_DOWN = "WestDown"
    EAST_DOWN = "EastDown"
    WEST_UP = "WestUp"
    EAST_UP = "EastUp"
    SECOND_MARK_UP = "SecondMarkUp"
    SECOND_MARK_DOWN = "SecondMarkDown"

    # meridian
    # meridian is the average of declination measurements
    # but recorded because calculated and used during inclination measurements.
    MERIDIAN = "Meridian"

    # inclination
    SOUTH_DOWN = "SouthDown"
    NORTH_UP = "NorthUp"
    SOUTH_UP = "SouthUp"
    NORTH_DOWN = "NorthDown"

    # scaling
    NORTH_DOWN_SCALE = "NorthDownScale"

    @property
    def direction(self):
        if self in [MeasurementType.SOUTH_DOWN, MeasurementType.NORTH_DOWN]:
            return 1
        else:
            return -1

    @property
    def shift(self):
        if self == MeasurementType.SOUTH_DOWN:
            return -200
        if self == MeasurementType.SOUTH_UP:
            return 200
        if self == MeasurementType.NORTH_UP:
            return 0
        if self == MeasurementType.NORTH_DOWN:
            return 400

    @property
    def meridian(self):
        if self in [
            MeasurementType.SOUTH_DOWN,
            MeasurementType.NORTH_UP,
            MeasurementType.EAST_UP,
            MeasurementType.EAST_DOWN,
        ]:
            return 1
        else:
            return -1
