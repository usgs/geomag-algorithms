#! /usr/bin/env python
from obspy.core.stream import Stream
from nose.tools import assert_equals
from nose.tools import assert_is
from geomagio import XYZAlgorithm
from StreamConverter_test import __create_trace


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
    assert_is(outputstream[0].stats.channel, 'X')


def test_xyzalgorithm_channels():
    """XYZAlgorithm_test.test_xyzalgorithm_channels()

    confirms that the input/output channels are correct for the given
    informat/outformat during instantiation.
    """
    algorithm = XYZAlgorithm('obs', 'geo')
    inchannels = ['H', 'E', 'Z', 'F']
    outchannels = ['X', 'Y', 'Z', 'F']
    assert_equals(algorithm.get_input_channels(), inchannels)
    assert_equals(algorithm.get_output_channels(), outchannels)
