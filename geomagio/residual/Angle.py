from typing import List


def from_dms(degrees: float = 0, minutes: float = 0, seconds: float = 0) -> float:
    """Convert degrees, minutes, seconds to decimal degrees"""
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def to_dms(degrees: float) -> List[float]:
    """Convert decimal degrees to degrees, minutes, seconds"""
    minutes = (degrees - int(degrees)) * 60
    seconds = (minutes - int(minutes)) * 60
    return [int(degrees), int(minutes), seconds]
