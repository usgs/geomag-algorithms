"""Tests for the IMFJSON Writer class."""

from numpy.testing import assert_equal
from geomagio.iaga2002 import IAGA2002Factory
from geomagio.imfjson import IMFJSONWriter
import numpy as np


EXAMPLE_INPUT_FACTORY = IAGA2002Factory()
EXAMPLE_CHANNELS = ('H', 'D', 'Z', 'F')
EXAMPLE_FILE = "etc/iaga2002/BOU/OneMinute/bou20141101vmin.min"
with open(EXAMPLE_FILE, "r") as input_file:
    data = input_file.read()
EXAMPLE_DATA = EXAMPLE_INPUT_FACTORY.parse_string(data)
EXAMPLE_STATS = EXAMPLE_DATA[0].stats


def test_metadata():
    """imfjson.IMFJSONWriter_test.test_metadata()

    Call the _format_metadata method with the test
    stats and channels.
    Verify, the set metadata.
    """
    writer = IMFJSONWriter()
    metadata = writer._format_metadata(EXAMPLE_STATS, EXAMPLE_CHANNELS)
    assert_equal(metadata['status'], 200)
    # Test intermagnet parameters
    intermag = metadata['intermagnet']
    assert_equal(intermag['reported_orientation'], "HDZF")
    assert_equal(intermag['sensor_orientation'], "HDZF")
    assert_equal(intermag['data_type'], "variation")
    assert_equal(intermag['sampling_period'], 60)
    assert_equal(intermag['digital_sampling_rate'], 0.01)
    # Test intermagnet-imo parameters
    imo = metadata['intermagnet']['imo']
    assert_equal(imo['iaga_code'], "BOU")
    assert_equal(imo['name'], "Boulder")
    assert_equal(imo['coordinates'], [254.764, 40.137, 1682])


def test_times():
    """imfjson.IMFJSONWriter_test.test_times()

    Call the _format_times method with the test
    data and channels.
    Verify, the times are the correct value and string format.
    """
    writer = IMFJSONWriter()
    times = writer._format_times(EXAMPLE_DATA, EXAMPLE_CHANNELS)
    # load times to test against
    test_day, test_time = np.genfromtxt(EXAMPLE_FILE, skip_header=25,
        usecols=(0, 1), unpack=True, dtype=str)
    test_date_times = []
    for idx in range(test_day.shape[0]):
        test_date_times += [test_day[idx] + "T" + test_time[idx] + "Z"]
    assert_equal(times, test_date_times)


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
            assert_equal(key, test)
    assert_equal(values[0]['id'], "H")
    assert_equal(values[1]['id'], "D")
    assert_equal(values[2]['id'], "Z")
    assert_equal(values[3]['id'], "F")
    # Test values-metadata (need to add flags)
    metadata = values[0]['metadata']
    test_metadata_keys = ["element", "network", "station",
            "channel", "location"]
    for key, test in zip(metadata, test_metadata_keys):
        assert_equal(key, test)
    assert_equal(metadata['element'], "H")
    assert_equal(metadata['network'], "NT")
    assert_equal(metadata['station'], "BOU")
    # channels do not match H v MVH
    # assert_equal(metadata['channel'], "MVH")
    assert_equal(metadata['location'], "R0")
    # Test values-values
    #  Round to match iaga format
    vals_H = np.around(values[0]['values'], 2)
    vals_D = np.around(values[1]['values'], 2)
    test_val_H, test_val_D = np.loadtxt(EXAMPLE_FILE, skiprows=25,
        usecols=(3, 4), unpack=True, dtype=float)
    #  tolist required to prevent ValueError in comparison
    assert_equal(vals_H.tolist(), test_val_H.tolist())
    assert_equal(vals_D.tolist(), test_val_D.tolist())
