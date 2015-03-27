#! /usr/bin/env python

"""Converts iaga2002 files from one coordinate system to another.

    Inputs
    ------
    inputFactory: TimeseriesFactory
    outputFactory: TimeseriesFactory
    algorithm: Algorithm
"""


class Controller(object):

    def __init__(self, inputFactory, outputFactory, algorithm=None):
        self._inputFactory = inputFactory
        self._algorithm = algorithm
        self._outputFactory = outputFactory

    def run(self, starttime, endtime):
        input_channels = self._algorithm.get_input_channels()
        timeseries = self._inputFactory.get_timeseries(starttime, endtime,
                channels=input_channels)
        if self._algorithm is not None:
            processed = self._algorithm.process(timeseries)
        else:
            processed = timeseries
        output_channels = self._algorithm.get_output_channels()
        self._outputFactory.put_timeseries(processed, channels=output_channels)
