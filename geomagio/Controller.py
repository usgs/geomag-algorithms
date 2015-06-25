"""Controller class for geomag algorithms"""

import TimeseriesUtilities


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

    def __init__(self, inputFactory, outputFactory, algorithm, update=False):
        self._inputFactory = inputFactory
        self._algorithm = algorithm
        self._outputFactory = outputFactory
        self._update = update

    def run(self, starttime, endtime):
        """run an algorithm as setup up by the main script.

        Parameters
        ----------
        starttime : UTCDateTime
            time of first sample to be worked on.
        endtime : UTCDateTime
            time of last sample to be worked on.
        """
        if (self._update):
            self.run_as_update(starttime, endtime)
        else:
            self.run_as_timeseries(starttime, endtime)

    def run_as_update(self, starttime, endtime):
        input_channels = self._algorithm.get_input_channels()
        output_channels = self._algorithm.get_output_channels()

        timeseries_in = self._inputFactory.get_timeseries(starttime,
                endtime, channels=input_channels)
        timeseries_out = self._inputFactory.get_timeseries(starttime,
                endtime, channels=output_channels)

        #TODO get input gaps

        output_gaps = TimeseriesUtilities.get_timeseries_gaps(
            timeseries_out, output_channels, starttime, endtime)

        output_merged_gaps = TimeseriesUtilities.get_merged_gaps(output_gaps,
                output_channels)
        # TODO compare gaps.
        #   if there is new data, run algorithm over entire time.
        #   save any new data.

        #TODO iterate is starttime of gaps is starttime and new data found


    def run_as_timeseries(self, starttime, endtime):
        input_channels = self._algorithm.get_input_channels()

        timeseries = self._inputFactory.get_timeseries(starttime, endtime,
            channels=input_channels)

        processed = self._algorithm.process(timeseries)
        output_channels = self._algorithm.get_output_channels()
        self._outputFactory.put_timeseries(timeseries=processed,
                channels=output_channels)
