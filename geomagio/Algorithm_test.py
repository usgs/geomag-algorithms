#! /usr/bin/env python
from obspy.core.stream import Stream
from nose.tools import assert_equals
from nose.tools import assert_is_instance
from Algorithm import Algorithm


def test_algorithm_process():
    """geomag.Algorithmtest.test_algorithm_process()

    confirms that algorithm.process returns an obspy.core.stream object
    """
    algorithm = Algorithm()
    timeseries = Stream()
    outputstream = algorithm.process(timeseries)
    assert_is_instance(outputstream, Stream)


def test_algorithm_channels():
    """geomag.Algorithmtest.test_algorithm_channels()

    confirms that algorithm.get_input_channels returns the correct channels
    confirms that algorithm.get_output_channels returns the correct channels
    """
    inchannels = ['H', 'E', 'Z', 'F']
    outchannels = ['H', 'D', 'Z', 'F']
    algorithm = Algorithm(inchannels=inchannels,
            outchannels=outchannels)
    assert_equals(algorithm.get_input_channels(), inchannels)
    assert_equals(algorithm.get_output_channels(), outchannels)
