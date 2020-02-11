#! /usr/bin/env python
from obspy.core.stream import Stream
from numpy.testing import assert_equal
from geomagio.algorithm import XYZAlgorithm
from ..StreamConverter_test import __create_trace
import numpy as np


def test_xyzalgorithm_process():
    """XYZAlgorithm_test.test_xyzalgorithm_process()

    confirms that a converted stream contains the correct outputchannels.
    """
    algorithm = XYZAlgorithm('obs', 'geo')
    timeseries = Stream()
    timeseries += __create_trace('H', [1, 1])
    timeseries += __create_trace('E', [1, 1])
    timeseries += __create_trace('Z', [1, 1])
    timeseries += __create_trace('F', [1, 1])
    outputstream = algorithm.process(timeseries)
    assert_equal(outputstream[0].stats.channel, 'X')


def test_xyzalgorithm_channels():
    """XYZAlgorithm_test.test_xyzalgorithm_channels()

    confirms that the input/output channels are correct for the given
    informat/outformat during instantiation.
    """
    algorithm = XYZAlgorithm('obs', 'geo')
    inchannels = ['H', 'E', 'Z', 'F']
    outchannels = ['X', 'Y', 'Z', 'F']
    assert_equal(algorithm.get_input_channels(), inchannels)
    assert_equal(algorithm.get_output_channels(), outchannels)


def test_xyzalgorithm_limited_channels():
    """XYZAlgorithm_test.test_xyzalgorithm_limited_channels()

    confirms that only the required channels are necessary for processing
    ie. 'H' and 'E' are only needed to get 'X' and 'Y' without 'Z' or 'F'
    """
    algorithm = XYZAlgorithm('obs', 'mag')
    count = 5
    timeseries = Stream()
    timeseries += __create_trace('H', [2] * count)
    timeseries += __create_trace('E', [3] * count)
    outstream = algorithm.process(timeseries)
    ds = outstream.select(channel='D')
    # there is 1 trace
    assert_equal(len(ds), 1)
    d = ds[0]
    # d has `count` values (same as input)
    assert_equal(len(d.data), count)
    # d has no NaN values
    assert_equal(np.isnan(d).any(), False)


def test_xyzalgorithm_uneccesary_channel_empty():
    """XYZAlgorithm_test.test_xyzalgorithm_uneccesary_channel_gaps()

    confirms the process will run when an uneccesary channel is input
    but contains gaps or is completely empty. ie. gaps in 'Z' channel
    or and empty 'F' channel. This also makes sure the 'Z' and 'F' channels
    are passed without any modification.
    """
    algorithm = XYZAlgorithm('obs', 'mag')
    timeseries = Stream()
    timeseries += __create_trace('H', [1, 1])
    timeseries += __create_trace('E', [1, 1])
    timeseries += __create_trace('Z', [1, np.NaN])
    timeseries += __create_trace('F', [np.NaN, np.NaN])
    outstream = algorithm.process(timeseries)
    assert_equal(outstream.select(channel='Z')[0].data.all(),
        timeseries.select(channel='Z')[0].data.all())
    assert_equal(outstream.select(channel='F')[0].data.all(),
        timeseries.select(channel='F')[0].data.all())
    ds = outstream.select(channel='D')
    # there is 1 trace
    assert_equal(len(ds), 1)
    d = ds[0]
    # d has 2 values (same as input)
    assert_equal(len(d.data), 2)
    # d has no NaN values
    assert_equal(np.isnan(d).any(), False)
