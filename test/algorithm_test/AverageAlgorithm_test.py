from geomagio.algorithm import AverageAlgorithm
from obspy.core.stream import Stream
from ..StreamConverter_test import __create_trace
from obspy.core import UTCDateTime
import numpy as np
from numpy.testing import assert_array_equal, assert_equal


def test_process():
    """AverageAlgorithm_test.test_process()
    confirms that the output of the algorithm is the average of three
    different stations.

    """
    # Make three test data arrays of 1's, 3's, and 5's
    # the average of the three arrays should be 3
    test_data1 = np.ones(5)
    test_data2 = np.ones(5) * 5
    test_data3 = np.ones(5) * 3

    # Create expected solution array of 3's
    expected_solution = np.ones(5) * 3

    # Create timeseries with first trace that uses test_data1
    timeseries = Stream()
    timeseries += __create_trace('H', test_data1)
    # Set metadata so process can read the array:
    # station, sample number, data type, and data interval
    timeseries[0].stats.station = 'HON'
    timeseries[0].stats.samples = 5
    timeseries[0].stats.data_type = 'variation'
    timeseries[0].stats.data_interval = 'minute'
    # Add the next trace with test_data2 and set station name
    timeseries += __create_trace('H', test_data2)
    timeseries[1].stats.station = 'GUA'
    # Add final trace with test_data3 and set station name
    timeseries += __create_trace('H', test_data3)
    timeseries[2].stats.station = 'SJG'

    # initialize the algorithm factory with Observatories and Channel
    a = AverageAlgorithm(('HON', 'GUA', 'SJG'), 'H')
    outstream = a.process(timeseries)
    # Ensure the average of two
    np.testing.assert_array_equal(outstream[0].data, expected_solution)


def test_gaps():
    """AverageAlgorithm_test.test_gaps()
    checks that gaps in data are not taken into account in
    the averaging process.

    """

    # Create a trace with data gaps
    gap_trace = __create_trace('H', [1, 1, np.nan, np.nan, 1, 1])

    # set time of first sample, sample rate (1 minute),
    # station, data type, and data interval
    gap_trace.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    gap_trace.stats.delta = 60
    gap_trace.stats.station = 'HON'
    gap_trace.stats.data_type = 'variation'
    gap_trace.stats.data_interval = 'minute'

    # Create a trace with no gaps
    full_trace = __create_trace('H', [1, 1, 1, 1, 1, 1])

    # set time of first sample, sample rate, station
    full_trace.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    full_trace.stats.delta = 60
    full_trace.stats.station = 'SJG'

    # Create timeseries that contains the gap_trace and full_trace
    timeseries = Stream()
    timeseries += gap_trace
    timeseries += full_trace
    # Initialize the AverageAlgorithm factory with observatories and channel
    alg = AverageAlgorithm(('HON', 'SJG'), 'H')
    # Run timeseries through the average process
    outstream = alg.process(timeseries)

    # The gaps should not be changed and should remain 'nan'
    assert_array_equal(outstream[0].data, [1, 1, np.nan, np.nan, 1, 1])


def test_metadata():
    """AverageAlgorithm_test.test_metadata()
    confirms the correct metadata is set for the
    resulting averaged data stream.

    """

    # Create a trace with channel 'H' and any numbers
    test_trace = __create_trace('H', [3, 3, 3, 3, 3, 3])
    test_trace2 = __create_trace('H', [1, 1, 1, 1, 1, 1])

    # set start time, sample rate (1 minute), station, data type and interval
    test_trace.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    test_trace.stats.delta = 60
    test_trace.stats.station = 'HON'
    test_trace.stats.data_type = 'variation'
    test_trace.stats.data_interval = 'minute'

    # set start time, sample rate (1 minute), station of second trace
    test_trace2.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    test_trace2.stats.delta = 60
    test_trace2.stats.station = 'SJG'

    # Populate timeseries with the 2 traces
    timeseries = Stream()
    timeseries += test_trace
    timeseries += test_trace2

    # Initialize the average algorithm with observatories and
    # set a new outchannel name
    alg = AverageAlgorithm(('HON', 'SJG'), 'Hdt')
    outstream = alg.process(timeseries)

    # The station name should be changed to 'USGS'
    assert_equal(outstream[0].stats.station, 'USGS')
    # The channel should be changed to 'Hdt'
    assert_equal(outstream[0].stats.channel, 'Hdt')
