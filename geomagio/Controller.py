"""Controller class for geomag algorithms"""

import numpy.ma as ma


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

        output_full_gaps, output_gaps = self._inputFactory.create_gap_stream(
                timeseries_out, output_channels)

        #self.get_gap_times(timeseries_out, output_channels)

        #starttime, endtime = self._algorithm.get_data_time_extent(channels, )

        #for each gap in start/end array
            # get corresponding input timeseries
            # processed = self._algorithm.process(timeseries)
            # self._outputFactory.put_timeseries(timeseries=processed,
                # channels=output_channels)

    def run_as_timeseries(self, starttime, endtime):
        input_channels = self._algorithm.get_input_channels()

        timeseries = self._inputFactory.get_timeseries(starttime, endtime,
            channels=input_channels)

        processed = self._algorithm.process(timeseries)
        output_channels = self._algorithm.get_output_channels()
        self._outputFactory.put_timeseries(timeseries=processed,
                channels=output_channels)

    def _convert_stream_to_masked(self, timeseries, channel):
        """convert geomag edge traces in a timeseries stream to a MaskedArray
            This allows for gaps and splitting.
        Parameters
        ----------
        stream : obspy.core.stream
            a stream retrieved from a geomag edge representing one channel.
        channel: string
            the channel to be masked.
        """
        for trace in timeseries.select(channel=channel):
            trace.data = ma.masked_invalid(trace.data)
