"""Conrtoller class for geomag algorithms"""


class Controller(object):
    """Controller for geomag algorithms.

    Parameters
    ----------
    inputFactory: TimeseriesFactory
        the factory that will read in timeseries data
    outputFactory: TimeseriesFactory
        the factory that will output the timeseries data
    algorithm: the algorithm(s) that will take procees the timeseries data
    """

    def __init__(self, inputFactory, outputFactory, algorithm):
        self._inputFactory = inputFactory
        self._algorithm = algorithm
        self._outputFactory = outputFactory

    def run(self, starttime, endtime):
        """run an algorithm as setup up by the main script.

        Parameters
        ----------
        starttime : UTCDateTime
            time of first sample to be worked on.
        endtime : UTCDateTime
            time of last sample to be worked on.
        """
        input_channels = self._algorithm.get_input_channels()
        timeseries = self._inputFactory.get_timeseries(starttime, endtime,
                channels=input_channels)
        processed = self._algorithm.process(timeseries)
        output_channels = self._algorithm.get_output_channels()
        self._outputFactory.put_timeseries(processed, channels=output_channels)
