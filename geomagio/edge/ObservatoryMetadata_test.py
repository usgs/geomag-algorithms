"""Tests for ObservatoryMetadata.py"""

from ObservatoryMetadata import ObservatoryMetadata
from nose.tools import assert_equals
import obspy.core


METADATA = {
    'BOU': {
        'network': 'NT',
        'station': 'BOU',
        'channel': 'H',
        'station_name': 'Boulder',
        'agency_name': 'United States Geological Survey (USGS)',
        'geodetic_latitude': -90,
        'geodetic_longitude': -180,
        'elevation': -1000,
        'sensor_orientation': 'HDZF',
        'sensor_sampling_rate': '0.01 second',
        'data_type': 'variation',
        'data_interval': 'minute',
        'data_interval_type': 'filtered 1-minute (00:15-01:45)',
        'declination_base': 20000,
        'is_intermagnet': False,
        'condtions_of_use': 'The Conditions of Use for data provided' +
                ' through INTERMAGNET and acknowledgement templates can be' +
                ' found at www.intermagnet.org',
        'filter_comments': 'Vector 1-minute values are computed from' +
                ' 1-second values using the INTERMAGNET gaussian filter' +
                ' centered on the  minute. Scalar 1-minute values are' +
                ' computed from 1-secondvalues  using the INTERMAGNET' +
                ' gaussian filter centered on the minute. ',
        'comments': ' # This data file was constructed by the Golden GIN.' +
                'Final data will be available on the INTERMAGNET DVD. Go to ' +
                'www.intermagnet.org for details on obtaining this product. '
    }
}


def test_set_metadata():
    """geomagio.edge.ObservatoryMetadata_test.test_set_metadata()
    """
    # Test set_metadata by passing in a stats class, and looking
    # for parameters that are both passed in, and aquired from the default
    # metadata.
    observatorymetadata = ObservatoryMetadata()
    stats = obspy.core.Stats()
    stats.channel = 'MVH'
    stats.location = 'R0'
    stats.data_interval = 'second'
    stats.data_type = 'quasi-definitive'
    observatorymetadata.set_metadata(stats, 'BOU')
    assert_equals(stats['channel'], 'MVH')
    assert_equals(stats['data_interval'], 'second')
    assert_equals(stats['data_type'], 'quasi-definitive')
    assert_equals(stats['declination_base'], 7406)

    # Test custom metadata
    stats = obspy.core.Stats()
    observatorymetadata = ObservatoryMetadata(METADATA)
    observatorymetadata.set_metadata(stats, 'BOU')
    assert_equals(stats['declination_base'], 20000)
