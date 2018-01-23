"""Tests for the IMFJSON Writer class."""

from nose.tools import assert_equals
from geomagio import edge
from geomagio.imfjson import IMFJSONWriter

from obspy.core import UTCDateTime

EXAMPLE_INPUT_FACTORY = edge.EdgeFactory()
EXAMPLE_CHANNELS = ('H', 'E', 'Z')
EXAMPLE_DATA = EXAMPLE_INPUT_FACTORY.get_timeseries(
    observatory='BOU',
    channels=EXAMPLE_CHANNELS,
    type='variation',
    interval='minute',
    starttime=UTCDateTime('2018-01-02'),
    endtime=UTCDateTime('2018-01-02T00:10:00'))
EXAMPLE_STATS = EXAMPLE_DATA[0].stats


def test_metadata():
    """imfjson.IMFJSONWriter_test.test_metadata()

    Call the _format_metadata method with the test
    stats and channels.
    Verify, the set metadata.
    """
    writer = IMFJSONWriter()
    metadata = writer._format_metadata(EXAMPLE_STATS, EXAMPLE_CHANNELS)
    assert_equals(metadata['status'], 200)
    # Test intermagnet parameters
    intermag = metadata['intermagnet']
    assert_equals(intermag['reported_orientation'], "HEZ")
    assert_equals(intermag['sensor_orientation'], "HDZF")
    assert_equals(intermag['sampling_period'], 60)
    assert_equals(intermag['digital_sampling_rate'], 0.01)
    # Test intermagnet-imo parameters
    imo = metadata['intermagnet']['imo']
    assert_equals(imo['iaga_code'], "BOU")
    assert_equals(imo['name'], "Boulder")
    assert_equals(imo['coordinates'], [254.763, 40.137, 1682])


def test_times():
    """imfjson.IMFJSONWriter_test.test_times()

    Call the _format_times method with the test
    data and channels.
    Verify, the times are the correct value and format.
    """
    writer = IMFJSONWriter()
    times = writer._format_times(EXAMPLE_DATA, EXAMPLE_CHANNELS)
    assert_equals(times, [
            "2018-01-02T00:00:00.000Z",
            "2018-01-02T00:01:00.000Z",
            "2018-01-02T00:02:00.000Z",
            "2018-01-02T00:03:00.000Z",
            "2018-01-02T00:04:00.000Z",
            "2018-01-02T00:05:00.000Z",
            "2018-01-02T00:06:00.000Z",
            "2018-01-02T00:07:00.000Z",
            "2018-01-02T00:08:00.000Z",
            "2018-01-02T00:09:00.000Z",
            "2018-01-02T00:10:00.000Z"
                            ])


def test_values():
    """imfjson.IMFJSONWriter_test.test_values()

    Call the _format_data method with the test
    data, channels, and stats.
    Verify, the values and associated metadata
    are the correct value and format.
    """
    writer = IMFJSONWriter()
    values = writer._format_data(EXAMPLE_DATA, EXAMPLE_CHANNELS,
            EXAMPLE_STATS)
    test_val_keys = ["id", "metadata", "values"]
    for val in values:
        for key, test in zip(val, test_val_keys):
            assert_equals(key, test)
    assert_equals(values[0]['id'], "H")
    assert_equals(values[1]['id'], "E")
    assert_equals(values[2]['id'], "Z")
    # Test values-metadata (need to add flags)
    metadata = values[0]['metadata']
    test_metadata_keys = ["element", "network", "station",
            "channel", "location"]
    for key, test in zip(metadata, test_metadata_keys):
        assert_equals(key, test)
    assert_equals(metadata['element'], "H")
    assert_equals(metadata['network'], "NT")
    assert_equals(metadata['station'], "BOU")
    # channels do not match H v MVH
    # assert_equals(metadata['channel'], "MVH")
    assert_equals(metadata['location'], "R0")
    # Test values-values
    vals = values[0]['values']
    assert_equals(vals, [
            20827.89,
            20827.982,
            20827.7,
            20827.542,
            20827.245,
            20826.802,
            20827.007,
            20826.774,
            20826.784,
            20826.946,
            20827.088
                            ])
