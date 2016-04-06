"""Controller class for geomag algorithms"""


import argparse
import sys
from obspy.core import Stream, UTCDateTime
from algorithm import algorithms
from PlotTimeseriesFactory import PlotTimeseriesFactory
import TimeseriesUtility

import edge
import iaga2002
import pcdcp
import imfv283


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

    def _get_input_timeseries(self, observatory, channels, starttime, endtime):
        """Get timeseries from the input factory for requested options.

        Parameters
        ----------
        observatory : array_like
            observatories to request.
        channels : array_like
            channels to request.
        starttime : obspy.core.UTCDateTime
            time of first sample to request.
        endtime : obspy.core.UTCDateTime
            time of last sample to request.
        renames : array_like
            list of channels to rename
            each list item should be array_like:
                the first element is the channel to rename,
                the last element is the new channel name

        Returns
        -------
        timeseries : obspy.core.Stream
        """
        timeseries = Stream()
        for obs in list(observatory):
            # get input interval for observatory
            # do this per observatory in case an
            # algorithm needs different amounts of data
            input_start, input_end = self._algorithm.get_input_interval(
                    start=starttime,
                    end=endtime,
                    observatory=obs,
                    channels=channels)
            timeseries += self._inputFactory.get_timeseries(
                    observatory=obs,
                    starttime=input_start,
                    endtime=input_end,
                    channels=channels)
        return timeseries

    def _rename_channels(self, timeseries, renames):
        """Rename trace channel names.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream with channels to rename
        renames : array_like
            list of channels to rename
            each list item should be array_like:
                the first element is the channel to rename,
                the last element is the new channel name

        Returns
        -------
        timeseries : obspy.core.Stream
        """
        for r in renames:
            from_name, to_name = r[0], r[-1]
            for t in timeseries.select(channel=from_name):
                t.stats.channel = to_name
        return timeseries

    def _get_output_timeseries(self, observatory, channels, starttime,
            endtime):
        """Get timeseries from the output factory for requested options.

        Parameters
        ----------
        observatory : array_like
            observatories to request.
        channels : array_like
            channels to request.
        starttime : obspy.core.UTCDateTime
            time of first sample to request.
        endtime : obspy.core.UTCDateTime
            time of last sample to request.

        Returns
        -------
        timeseries : obspy.core.Stream
        """
        timeseries = Stream()
        for obs in list(observatory):
            timeseries += self._outputFactory.get_timeseries(
                observatory=obs,
                starttime=starttime,
                endtime=endtime,
                channels=channels)
        return timeseries

    def run(self, options):
        """run controller
        Parameters
        ----------
        options: dictionary
            The dictionary of all the command line arguments. Could in theory
            contain other options passed in by the controller.
        """
        algorithm = self._algorithm
        input_channels = options.inchannels or \
                algorithm.get_input_channels()
        output_channels = options.outchannels or \
                algorithm.get_output_channels()
        # input
        timeseries = self._get_input_timeseries(
                observatory=options.observatory,
                starttime=options.starttime,
                endtime=options.endtime,
                channels=input_channels)
        if timeseries.count() == 0:
            return
        # process
        if options.rename_input_channel:
            timeseries = self._rename_channels(
                    timeseries=timeseries,
                    renames=options.rename_input_channel)
        processed = algorithm.process(timeseries)
        # trim if --no-trim is not set
        if not options.no_trim:
            processed.trim(starttime=options.starttime,
                    endtime=options.endtime)
        if options.rename_output_channel:
            processed = self._rename_channels(
                    timeseries=processed,
                    renames=options.rename_output_channel)
        # output
        self._outputFactory.put_timeseries(
                timeseries=processed,
                starttime=options.starttime,
                endtime=options.endtime,
                channels=output_channels)

    def run_as_update(self, options, update_count=0):
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
        # If an update_limit is set, make certain we don't step past it.
        if options.update_limit != 0:
            if update_count >= options.update_limit:
                return
        algorithm = self._algorithm
        input_channels = options.inchannels or \
                algorithm.get_input_channels()
        output_channels = options.outchannels or \
                algorithm.get_output_channels()
        # request output to see what has already been generated
        output_timeseries = self._get_output_timeseries(
                observatory=options.observatory,
                starttime=options.starttime,
                endtime=options.endtime,
                channels=output_channels)
        delta = output_timeseries[0].stats.delta
        # find gaps in output, so they can be updated
        output_gaps = TimeseriesUtility.get_merged_gaps(
                TimeseriesUtility.get_stream_gaps(output_timeseries))
        for output_gap in output_gaps:
            input_timeseries = self._get_input_timeseries(
                    observatory=options.observatory,
                    starttime=output_gap[0],
                    endtime=output_gap[1],
                    channels=input_channels)
            if not algorithm.can_produce_data(
                    starttime=output_gap[0],
                    endtime=output_gap[1],
                    stream=input_timeseries):
                continue
            # check for fillable gap at start
            if output_gap[0] == options.starttime:
                # found fillable gap at start, recurse to previous interval
                interval = options.endtime - options.starttime
                starttime = options.starttime - interval - delta
                endtime = options.starttime - delta
                options.starttime = starttime
                options.endtime = endtime
                self.run_as_update(options, update_count + 1)
            # fill gap
            options.starttime = output_gap[0]
            options.endtime = output_gap[1]
            self.run(options)


def main(args):
    """command line factory for geomag algorithms

    Inputs
    ------
    use geomag.py --help to see inputs, or see parse_args.

    Notes
    -----
    parses command line options using argparse, then calls the controller
    with instantiated I/O factories, and algorithm(s)
    """

    # Input Factory
    if args.input_edge is not None:
        inputfactory = edge.EdgeFactory(
                host=args.input_edge,
                port=args.input_edge_port,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval,
                locationCode=args.locationcode)
    elif args.input_iaga_file is not None:
        inputfactory = iaga2002.StreamIAGA2002Factory(
                stream=open(args.input_iaga_file, 'r'),
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    # TODO remove magweb option
    elif args.input_iaga_magweb:
        inputfactory = iaga2002.MagWebFactory(
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.input_iaga_stdin:
        inputfactory = iaga2002.StreamIAGA2002Factory(
                stream=sys.stdin,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.input_iaga_url is not None:
        inputfactory = iaga2002.IAGA2002Factory(
                urlTemplate=args.input_iaga_url,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.input_imfv283_file is not None:
        inputfactory = imfv283.StreamIMFV283Factory(
                stream=open(args.input_imfv283_file, 'r'),
                observatory=args.observatory)
    elif args.input_imfv283_goes:
        inputfactory = imfv283.GOESIMFV283Factory(
                directory=args.input_goes_directory,
                getdcpmessages=args.input_goes_getdcpmessages,
                observatory=args.observatory,
                server=args.input_goes_server,
                user=args.input_goes_user)
    elif args.input_imfv283_stdin:
        inputfactory = imfv283.StreamIMFV283Factory(
                stream=sys.stdin,
                observatory=args.observatory)
    elif args.input_imfv283_url is not None:
        inputfactory = imfv283.IMFV283Factory(
                urlTemplate=args.input_imfv283_url,
                observatory=args.observatory)
    elif args.input_pcdcp_file is not None:
        inputfactory = pcdcp.StreamPCDCPFactory(
                stream=open(args.input_pcdcp_file, 'r'),
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.input_pcdcp_stdin:
        inputfactory = pcdcp.StreamPCDCPFactory(
                stream=sys.stdin,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.input_pcdcp_url is not None:
        inputfactory = pcdcp.PCDCPFactory(
                urlTemplate=args.input_pcdcp_url,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    else:
        print >> sys.stderr, 'Missing required input directive.'

    # Output Factory
    if args.output_iaga_file is not None:
        outputfactory = iaga2002.StreamIAGA2002Factory(
                stream=open(args.output_iaga_file, 'wb'),
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.output_iaga_stdout:
        outputfactory = iaga2002.StreamIAGA2002Factory(
                stream=sys.stdout,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.output_iaga_url is not None:
        outputfactory = iaga2002.IAGA2002Factory(
                urlTemplate=args.output_iaga_url,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.output_pcdcp_file is not None:
        outputfactory = pcdcp.StreamPCDCPFactory(
                stream=open(args.output_pcdcp_file, 'wb'),
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.output_pcdcp_stdout:
        outputfactory = pcdcp.StreamPCDCPFactory(
                stream=sys.stdout,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.output_pcdcp_url is not None:
        outputfactory = pcdcp.PCDCPFactory(
                urlTemplate=args.output_pcdcp_url,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
    elif args.output_edge is not None:
        locationcode = args.outlocationcode or args.locationcode or None
        outputfactory = edge.EdgeFactory(
                host=args.output_edge,
                port=args.output_edge_read_port,
                write_port=args.edge_write_port,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval,
                locationCode=locationcode,
                tag=args.output_edge_tag,
                forceout=args.output_edge_forceout)
    elif args.output_plot:
        outputfactory = PlotTimeseriesFactory()
    else:
            print >> sys.stderr, "Missing required output directive"

    algorithm = algorithms[args.algorithm]()
    algorithm.configure(args)

    # TODO check for unused arguments.

    if (args.realtime):
        now = UTCDateTime()
        args.endtime = UTCDateTime(now.year, now.month, now.day,
                now.hour, now.minute)
        if args.interval == 'minute':
            args.starttime = args.endtime - 3600
        else:
            args.starttime = args.endtime - 600
        print args.starttime, args.endtime

    controller = Controller(inputfactory, outputfactory, algorithm)

    if args.update:
        controller.run_as_update(args)
    else:
        controller.run(args)


def parse_args(args):
    """parse input arguments

    Parameters
    ----------
    args : list of strings

    Returns
    -------
    argparse.Namespace
        dictionary like object containing arguments.
    """
    parser = argparse.ArgumentParser(
        description='Use @ to read commands from a file.',
        fromfile_prefix_chars='@',)

    parser.add_argument('--starttime',
            type=UTCDateTime,
            default=None,
            help='UTC date YYYY-MM-DD HH:MM:SS')
    parser.add_argument('--endtime',
            type=UTCDateTime,
            default=None,
            help='UTC date YYYY-MM-DD HH:MM:SS')

    parser.add_argument('--observatory',
            help='Observatory code ie BOU, CMO, etc.' +
                    ' CAUTION: Using multiple observatories is not' +
                    ' recommended in most cases; especially with' +
                    ' single observatory formats like IAGA and PCDCP.',
            nargs='*')
    parser.add_argument('--inchannels',
            nargs='*',
            help='Channels H, E, Z, etc')
    parser.add_argument('--outchannels',
            nargs='*',
            default=None,
            help='Channels H, E, Z, etc')
    parser.add_argument('--type',
            default='variation',
            choices=['variation', 'quasi-definitive', 'definitive'])
    parser.add_argument('--rename-input-channel',
            action='append',
            help='Rename an input channel after it is read',
            metavar=('FROM', 'TO'),
            nargs=2)
    parser.add_argument('--rename-output-channel',
            action='append',
            help='Rename an output channel before it is written',
            metavar=('FROM', 'TO'),
            nargs=2)
    parser.add_argument('--locationcode',
            choices=['R0', 'R1', 'RM', 'Q0', 'D0', 'C0'])
    parser.add_argument('--outlocationcode',
            choices=['R0', 'R1', 'RM', 'Q0', 'D0', 'C0'])
    parser.add_argument('--interval',
            default='minute',
            choices=['hourly', 'minute', 'second'])
    parser.add_argument('--update',
            action='store_true',
            default=False,
            help='Used to update data')
    parser.add_argument('--update-limit',
            type=int,
            default=0,
            help='Used to limit the number of iterations update will recurse')
    parser.add_argument('--no-trim',
            action='store_true',
            default=False,
            help='Ensures output data will not be trimmed down'),
    parser.add_argument('--input-edge-port',
            type=int,
            default=2060,
            help='Input port # for edge input, defaults to 2060')
    parser.add_argument('--output-edge-port',
            type=int,
            dest='edge_write_port',
            default=7981,
            help='Edge port for writing realtime data, defaults to 7981')
    parser.add_argument('--output-edge-cwb-port',
            type=int,
            dest='edge_write_port',
            default='7981',
            help='Edge port for writing older data. Not used by geomag.')
    parser.add_argument('--output-edge-read-port',
            type=int,
            default=2060,
            help='Edge port for reading output data, defaults to 2060')
    parser.add_argument('--output-edge-tag',
            default='GEOMAG',
            help='ID Tag for edge connections, defaults to GEOMAG')
    parser.add_argument('--output-edge-forceout',
            action='store_true',
            default=False,
            help='Flag to force data into miniseed blocks. Should only ' +
                    'be used when certain the data is self contained.')
    parser.add_argument('--realtime',
            action='store_true',
            default=False,
            help='Flag to run the last hour if interval is minute, ' +
                    'or the last 10 minutes if interval is seconds')
    parser.add_argument('--input-goes-directory',
            default='.',
            help='Directory for support files for goes input of imfv283 data')
    parser.add_argument('--input-goes-getdcpmessages',
            default='',
            help='Location of getDcpMessages.')
    parser.add_argument('--input-goes-server',
            nargs='*',
            help='The server name(s) to retrieve the GOES data from')
    parser.add_argument('--input-goes-user',
            default='GEOMAG',
            help='The user name to use to retrieve data from GOES')

    # Input group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input-edge',
            help='Host IP #, see --input-edge-port for optional args')
    input_group.add_argument('--input-iaga-file',
            help='Reads from the specified file.')
    input_group.add_argument('--input-iaga-magweb',
            action='store_true',
            default=False,
            help='Indicates iaga2002 files will be read from \
            http://magweb.cr.usgs.gov/data/magnetometer/')
    input_group.add_argument('--input-iaga-stdin',
            action='store_true',
            default=False,
            help='Pass in an iaga file using redirection from stdin.')
    input_group.add_argument('--input-iaga-url',
            help='Example: file://./%%(obs)s%%(ymd)s%%(t)s%%(i)s.%%(i)s')
    input_group.add_argument('--input-imfv283-file',
            help='Reads from the specified file.')
    input_group.add_argument('--input-imfv283-stdin',
            action='store_true',
            default=False,
            help='Pass in a file using redirection from stdin')
    input_group.add_argument('--input-imfv283-url',
            help='Example file://./')
    input_group.add_argument('--input-imfv283-goes',
            action='store_true',
            default=False,
            help='Retrieves data directly from a goes server to read')
    input_group.add_argument('--input-pcdcp-file',
            help='Reads from the specified file.')
    input_group.add_argument('--input-pcdcp-stdin',
            action='store_true',
            default=False,
            help='Pass in an pcdcp file using redirection from stdin.')
    input_group.add_argument('--input-pcdcp-url',
            help='Example: file://./%%(obs)s%%(Y)s%%(j)s.%%(i)s')

    # Output group
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument('--output-iaga-file',
            help='Write to a single iaga file.')
    output_group.add_argument('--output-iaga-stdout',
            action='store_true', default=False,
            help='Write to stdout.')
    output_group.add_argument('--output-iaga-url',
            help='Example: file://./%%(obs)s%%(ymd)s%%(t)s%%(i)s.%%(i)s')
    output_group.add_argument('--output-pcdcp-file',
            help='Write to a single pcdcp file.')
    output_group.add_argument('--output-pcdcp-stdout',
            action='store_true', default=False,
            help='Write to stdout.')
    output_group.add_argument('--output-pcdcp-url',
            help='Example: file://./%%(obs)s%%(Y)s%%(j)s.%%(i)s')
    output_group.add_argument('--output-edge',
            help='Edge IP #. See --output-edge-* for other optional arguments')
    output_group.add_argument('--output-plot',
            action='store_true',
            default=False,
            help='Plot the algorithm output using matplotlib')

    # Algorithms group
    parser.add_argument('--algorithm',
            choices=[k for k in algorithms],
            default='identity')

    for k in algorithms:
        algorithms[k].add_arguments(parser)

    return parser.parse_args(args)
