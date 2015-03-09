"""Tests for ObservatoryMetadata.py"""

from ObservatoryMetadata import ObservatoryMetadata
from nose.tools import assert_equals
import obspy.core


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
    stats = observatorymetadata.set_metadata(stats, 'BOU', 'H',
            'quasi-definitive', 'second')
    assert_equals(stats['channel'], 'MVH')
    assert_equals(stats['data_interval'], 'second')
    assert_equals(stats['data_type'], 'quasi-definitive')
    assert_equals(stats['declination_base'], 7406)
