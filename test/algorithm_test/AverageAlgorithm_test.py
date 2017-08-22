from geomagio.algorithm import AverageAlgorithm as avg
from obspy.core.stream import Stream
from ..StreamConverter_test import __create_trace
from obspy.core import UTCDateTime
from nose.tools import assert_equals
import numpy as np
from numpy.testing import assert_array_equal
# from nose.tools import assert_almost_equals


def test_process():
    """AverageAlgorithm_test.test_process()
    confirms that the output of the algorithm is the average of three
    different stations.

    """

    dat1 = np.array(np.ones(5))
    dat2 = np.ones(5) * 5
    dat3 = np.ones(5) * 3
    final_data = np.ones(5) * 3
    timeseries = Stream()
    timeseries += __create_trace('H', dat1)
    timeseries[0].stats.station = 'HON'
    timeseries[0].stats.samples = 5
    timeseries[0].stats.data_type = 'variation'
    timeseries[0].stats.data_interval = 'minute'
    timeseries += __create_trace('H', dat2)
    timeseries[1].stats.station = 'GUA'
    timeseries += __create_trace('H', dat3)
    timeseries[2].stats.station = 'SJG'
    a = avg(('HON', 'GUA', 'SJG'), 'H')
    outstream = a.process(timeseries)
    # Ensure the average of two
    np.testing.assert_array_equal(outstream[0].data, final_data)


def test_gaps():
    """AverageAlgorithm_test.test_gaps()
    checks that gaps in data are not taken into account in
    the averaging process.

    """

    trace1 = __create_trace('H', [1, 1, np.nan, np.nan, 1, 1])
    # set time of first sample
    trace1.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    # set sample rate to 1 minute
    trace1.stats.delta = 60
    # set station code
    trace1.stats.station = 'HON'
    trace1.stats.data_type = 'variation'
    trace1.stats.data_interval = 'minute'

    trace2 = __create_trace('H', [1, 1, 1, 1, 1, 1])
    # set time of first sample
    trace2.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    # set sample rate to 1 minute
    trace2.stats.delta = 60
    # set station code
    trace2.stats.station = 'SJG'

    timeseries = Stream()
    timeseries += trace1
    timeseries += trace2
    alg = avg(('HON', 'SJG'), 'H')
    outstream = alg.process(timeseries)

    assert_array_equal(outstream[0].data, [1, 1, np.nan, np.nan, 1, 1])


def test_metadata():
    """AverageAlgorithm_test.test_metadata()
    confirms the correct metadata is set for the
    resulting averaged data stream.

    """

    trace1 = __create_trace('H', [3, 3, 3, 3, 3, 3])
    # set time of first sample
    trace1.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    # set sample rate to 1 minute
    trace1.stats.delta = 60
    # set station code
    trace1.stats.station = 'HON'
    trace1.stats.data_type = 'variation'
    trace1.stats.data_interval = 'minute'

    trace2 = __create_trace('H', [1, 1, 1, 1, 1, 1])
    # set time of first sample
    trace2.stats.starttime = UTCDateTime('2015-01-01T00:00:00Z')
    # set sample rate to 1 minute
    trace2.stats.delta = 60
    # set station code
    trace2.stats.station = 'SJG'

    timeseries = Stream()
    timeseries += trace1
    timeseries += trace2

    alg = avg(('HON', 'SJG'), 'Hdt')
    outstream = alg.process(timeseries)

    assert_equals(outstream[0].stats.station, 'USGS')
    assert_equals(outstream[0].stats.channel, 'Hdt')
