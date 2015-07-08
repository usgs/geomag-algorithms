"""Controller class for geomag algorithms"""

import TimeseriesUtility
import TimeseriesFactoryException


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

    Notes
    -----
    Has 2 basic modes.
    Run simply sends all the data in a stream to edge. If a startime/endtime is
        provided, it will send the data from the stream that is within that
        time span.
    Update will update any data that has changed between the source, and
        the target during a given timeframe. It will also attempt to
        recursively backup so it can update all missing data.
    """

    def __init__(self, inputFactory, outputFactory, algorithm):
        self._inputFactory = inputFactory
        self._algorithm = algorithm
        self._outputFactory = outputFactory

    def run(self, options):
        """run controller
        Parameters
        ----------
        options: dictionary
            The dictionary of all the command line arguments. Could in theory
            contain other options passed in by the controller.
        """
        algorithm = self._algorithm
        input_channels = algorithm.get_input_channels()
        output_channels = self._get_output_channels(
                algorithm.get_output_channels(),
                options.outchannels)
        # get input
        start, end = self._algorithm.get_input_interval(
                start=options.starttime,
                end=options.endtime)
        timeseries = self._inputFactory.get_timeseries(
                starttime=start,
                endtime=end,
                channels=input_channels)
        # process
        processed = algorithm.process(timeseries)
        # output
        self._outputFactory.put_timeseries(
                timeseries=processed,
                starttime=options.starttime,
                endtime=options.endtime,
                channels=output_channels)

    def run_as_update(self, options):
        """Updates data.
        Parameters
        ----------
        options: dictionary
            The dictionary of all the command line arguments. Could in theory
            contain other options passed in by the controller.

        Notes
        -----
        Finds gaps in the target data, and if there's new data in the input
            source, calls run with the start/end time of a given gap to fill
            in.
        It checks the start of the target data, and if it's missing, and
            there's new data available, it backs up the starttime/endtime,
            and recursively calls itself, to check the previous period, to see
            if new data is available there as well. Calls run for each new
            period, oldest to newest.
        """
        algorithm = self._algorithm
        input_channels = algorithm.get_input_channels()
        output_channels = self._get_output_channels(
                algorithm.get_output_channels(),
                options.outchannels)
        # request output to see what has already been generated
        output_timeseries = self._outputFactory.get_timeseries(
                starttime=options.starttime,
                endtime=options.endtime,
                channels=output_channels)
        # find gaps in output, so they can be updated
        output_gaps = TimeseriesUtility.get_stream_gaps(output_timeseries)
        for gap in output_gaps:
            start, end = algorithm.get_input_interval(
                    start=gap[0],
                    end=gap[1])
            input_timeseries = self._inputFactory.get_timeseries(
                    starttime=start,
                    endtime=end,
                    channels=input_channels)
            input_gaps = TimeseriesUtility.get_stream_gaps(input_timeseries)
            if len(input_gaps) > 0:
                # TODO: are certain gaps acceptable?
                continue
            # check for fillable gap at start
            if gap[0] == options.starttime:
                # found fillable gap at start, recurse to previous interval
                interval = options.endtime - options.starttime
                self.run_as_update({
                    'outchannels': options.outchannels,
                    'starttime': options.starttime - interval,
                    'endtime': options.starttime
                })
            # fill gap
            self.run({
                'outchannels': options.outchannels,
                'starttime': gap[0],
                'endtime': gap[1]
            })

    def _get_output_channels(self, algorithm_channels, commandline_channels):
        """get output channels

        Parameters
        ----------
        algorithm_channels: array_like
            list of channels required by the algorithm
        commandline_channels: array_like
            list of channels requested by the user
        Notes
        -----
        We want to return the channels requested by the user, but we require
            that they be in the list of channels for the algorithm.
        """
        if commandline_channels is not None:
            for channel in commandline_channels:
                if channel not in algorithm_channels:
                    raise TimeseriesFactoryException(
                        'Output "%s" Channel not in Algorithm'
                            % channel)
            return commandline_channels
        return algorithm_channels
