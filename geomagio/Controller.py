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
    algorithm: the algorithm(s) that will take procees the timeseries data
    """

    def __init__(self, inputFactory, outputFactory, algorithm, update=False,
            interval='minute', update_realtime=False):
        self._inputFactory = inputFactory
        self._algorithm = algorithm
        self._outputFactory = outputFactory
        self._update = update
        self._interval = interval
        self._update_realtime = update_realtime

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
        seconds_of_interval = TUtils.get_seconds_of_interval(self._interval)
        backup_start = starttime
        backup_end = endtime
        backup = self._update_realtime

        # get new input_channel data, and last output data.
        timeseries_in = self._inputFactory.get_timeseries(backup_start,
                endtime, channels=input_channels)
        timeseries_update = self._outputFactory.get_timeseries(backup_start,
                endtime, channels=output_channels)
        # repeat until ouput is succesfully backfilled.
        while backup:
            first_in_exists = self._first_value_exists(timeseries_in,
                    input_channels)
            first_out_exists = self._first_value_exists(timeseries_update,
                    output_channels)
            if first_in_exists and not first_out_exists:
                new_backup_end = backup_start - seconds_of_interval
                backup_start = backup_start - (backup_end - backup_start)
                backup_end = new_backup_end
                timeseries_in += self._inputFactory.get_timeseries(
                        backup_start, backup_end, channels=input_channels)
                timeseries_update += self._outputFactory.get_timeseries(
                        backup_start, backup_end, channels=output_channels)
                timeseries_in.merge()
                timeseries_update.merge()
            else:
                backup = False
            print backup_start, backup_end
        starttime = backup_start

        input_gaps = TUtils.get_timeseries_gaps(
            timeseries_in, input_channels, starttime, endtime)
        output_gaps = TUtils.get_timeseries_gaps(
            timeseries_update, output_channels, starttime, endtime)

        input_merged_gaps = TUtils.get_merged_gaps(
                input_gaps, input_channels)
        output_merged_gaps = TUtils.get_merged_gaps(
                output_gaps, output_channels)

        if TUtils.is_new_data(input_merged_gaps, output_merged_gaps):
            pass

            # TODO call algorithm

            # TODO call output

    def _first_value_exists(self, timeseries, channels):
        for channel in channels:
            stream = timeseries.select(channel=channel)
            if len(stream[0].data) and not numpy.isnan(stream[0].data[0]):
                return True
        return False


    def run_as_timeseries(self, starttime, endtime):
        input_channels = self._algorithm.get_input_channels()

        timeseries = self._inputFactory.get_timeseries(starttime, endtime,
            channels=input_channels)

        processed = self._algorithm.process(timeseries)
        output_channels = self._algorithm.get_output_channels()
        self._outputFactory.put_timeseries(timeseries=processed,
                channels=output_channels)
