"""Tests for ObservatoryMetadata.py"""

from geomagio import ObservatoryMetadata
from numpy.testing import assert_equal
import obspy.core

DEFAULT_INTERVAL_SPECIFIC = {
    "day": {
        "data_interval_type": "1-day (00:00-23:59)",
        "filter_comments": [
            "Scalar and Vector 1-day values are computed from average of 1-minute values in the day (00:00-23:59)",
        ],
    },
    "hour": {
        "data_interval_type": "1-hour (00-59)",
        "filter_comments": [
            "Scalar and Vector 1-hour values are computed from average of 1-minute values in the hour (00-59)",
        ],
    },
    "minute": {
        "data_interval_type": "1-minute",
        "filter_comments": [
            "Scalar and Vector 1-minute values are computed from 1 Hz values using an INTERMAGNET gaussian filter centered on the start of the minute (00:30-01:30)."
        ],
    },
    "second": {
        "data_interval_type": "1-second",
        "filter_comments": [
            "Vector 1-second values are computed from 10 Hz values using a Blackman filter (123 taps, cutoff 0.25Hz) centered on the start of the second."
        ],
    },
}

METADATA = {
    "BOU": {
        "metadata": {
            "station_name": "Boulder",
            "agency_name": "United States Geological Survey (USGS)",
            "geodetic_latitude": "-90",
            "geodetic_longitude": "-180",
            "elevation": "-1000",
            "sensor_orientation": "HDZF",
            "sensor_sampling_rate": "0.01 second",
            "declination_base": 20000,
            "is_gin": False,
            "is_intermagnet": False,
            "conditions_of_use": "The Conditions of Use for data provided"
            + " through INTERMAGNET and acknowledgement templates"
            + " can be found at www.intermagnet.org",
        },
        "interval_specific": DEFAULT_INTERVAL_SPECIFIC,
    }
}


DATA_INTERVAL_TYPE = {
    "day": {"data_interval_type": "1-day"},
    "hour": {"data_interval_type": "1-hour"},
    "minute": {"data_interval_type": "1-minute"},
    "second": {"data_interval_type": "1-second"},
}


def test_set_metadata():
    """ObservatoryMetadata_test.test_set_metadata()"""
    # Test set_metadata by passing in a stats class, and looking
    # for parameters that are both passed in, and aquired from the default
    # metadata.
    observatorymetadata = ObservatoryMetadata()
    stats = obspy.core.Stats()
    stats.channel = "MVH"
    stats.location = "R0"
    stats.data_interval = "second"
    stats.data_type = "quasi-definitive"
    observatorymetadata.set_metadata(stats, "BOU", "MVH", "quasi-definitive", "second")
    assert_equal(stats["declination_base"], 5527)

    # Test custom metadata
    stats = obspy.core.Stats()
    observatorymetadata = ObservatoryMetadata(METADATA, DATA_INTERVAL_TYPE)
    observatorymetadata.set_metadata(stats, "BOU", "MVH", "quasi-definitive", "second")
    assert_equal(stats["declination_base"], 20000)
    print(stats)
    assert_equal(stats["data_interval_type"], "1-second")
