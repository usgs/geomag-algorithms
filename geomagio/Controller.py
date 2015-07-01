"""Controller class for geomag algorithms"""

import TimeseriesUtilities as TUtils
import numpy
import obspy


class Controller(object):
    """Controller for geomag algorithms.

    Parameters
    ----------
    inputFactory: TimeseriesFactory
        the factory that will read in timeseries data
    outputFactory: TimeseriesFactory
        the factory that will output the timeseries data
    algorithm: Algorithm
        the algorithm(s) that will procees the timeseries data
    update: boolean
        indicates that data is to be updated.
    interval: string
        the data interval {daily, hourly, minute, second}
    update_realtime: boolean
        indicates

    Notes
    -----
    Has 2(3) basic modes.
    Run simply sends all the data in a stream to edge. If a startime/endtime is
        provided, it will send the data from the stream that is within that
        time span.
    Update will update any data that has changed between the source, and
        the target during a given timeframe. If the update_realtime flag
        is set, it will attempt to recursively backup so it can update all
        missing data.
    """

    def __init__(self, inputFactory, outputFactory, algorithm, update=False,
            interval='minute', update_realtime=False):
        self._inputFactory = inputFactory
        self._algorithm = algorithm
        self._outputFactory = outputFactory
        self._update = update
        self._interval = interval
        self._update_realtime = update_realtime
        self._interval_in_seconds = TUtils.get_seconds_of_interval(interval)

    def run(self, starttime, endtime):
        """run controller
        Parameters
        ----------
        starttime: obspy.core.UTCDateTime
            time of first sample. None if starttime should come from dataset
        endtime: obspy.core.UTCDateTime
            endtime of last sampel.  None if endtime should come from dataset
        """
        input_channels = self._algorithm.get_input_channels()
        algorithm_start, algorithm_end = self._algorithm.get_input_interval(
                starttime, endtime)

        timeseries = self._inputFactory.get_timeseries(algorithm_start,
            algorithm_end, channels=input_channels)

        processed = self._algorithm.process(timeseries)
        output_channels = self._algorithm.get_output_channels()

        self._outputFactory.put_timeseries(timeseries=processed,
                starttime=starttime, endtime=endtime,
                channels=output_channels)

    def run_as_update(self, starttime, endtime):
        """Updates data.
        Parameters
        ----------
        starttime: obspy.core.UTCDateTime
            time of first sample. None if starttime should come from dataset
        endtime: obspy.core.UTCDateTime
            endtime of last sampel.  None if endtime should come from dataset

        Notes
        -----
        Finds gaps in the target data, and if there's new data in the input
            source, calls run with the start/end time of a given gap to fill
            in.
        If the update_realtime flag is set, it checks the start of the target
            data, and if it's missing, and there's new data available, it backs
            up the starttime/endtime, and recursively calls itself, to check
            the previous period, to see if new data is available there as well.
            Calls run for each new period, oldest to newest.
        """
        input_channels = self._algorithm.get_input_channels()
        output_channels = self._algorithm.get_output_channels()

        timeseries_source = self._inputFactory.get_timeseries(starttime,
                endtime, channels=input_channels)
        timeseries_target = self._outputFactory.get_timeseries(starttime,
                endtime, channels=output_channels)

        source_gaps = TUtils.get_timeseries_gaps(
            timeseries_source, input_channels, starttime, endtime)
        target_gaps = TUtils.get_timeseries_gaps(
            timeseries_target, output_channels, starttime, endtime)
        source_gaps = TUtils.get_merged_gaps(
                source_gaps, input_channels)
        target_gaps = TUtils.get_merged_gaps(
                target_gaps, output_channels)
        del timeseries_source
        del timeseries_target
        if (self._update_realtime and
                (not len(source_gaps) or
                len(source_gaps) and source_gaps[0][0] != starttime) and
                len(target_gaps) and target_gaps[0][0] == starttime):
            self.run_as_update((starttime - (endtime - starttime)),
                (starttime - self._interval_in_seconds))
        for target_gap in target_gaps:
            if not TUtils.gap_is_new_data(source_gaps, target_gap):
                continue
            self.run(target_gap[0], target_gap[1])
