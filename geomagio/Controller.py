"""Controller class for geomag algorithms"""
from __future__ import absolute_import, print_function
from builtins import str as unicode

import argparse
import sys
from io import BytesIO
from obspy.core import Stream, UTCDateTime
from .algorithm import algorithms, AlgorithmException
from .PlotTimeseriesFactory import PlotTimeseriesFactory
from .StreamTimeseriesFactory import StreamTimeseriesFactory
from . import TimeseriesUtility, Util

# factory packages
from . import binlog
from . import edge
from . import iaga2002
from . import imfjson
from . import pcdcp
from . import imfv122
from . import imfv283
from . import temperature
from . import vbf


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
        for obs in observatory:
            # get input interval for observatory
            # do this per observatory in case an
            # algorithm needs different amounts of data
            input_start, input_end = self._algorithm.get_input_interval(
                    start=starttime,
                    end=endtime,
                    observatory=obs,
                    channels=channels)
            if input_start is None or input_end is None:
                continue
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
        for obs in observatory:
            timeseries += self._outputFactory.get_timeseries(
                observatory=obs,
                starttime=starttime,
                endtime=endtime,
                channels=channels)
        return timeseries

    def run(self, options, input_timeseries=None):
        """run controller
        Parameters
        ----------
        options: dictionary
            The dictionary of all the command line arguments. Could in theory
            contain other options passed in by the controller.
        input_timeseries : obspy.core.Stream
            Used by run_as_update to save a double input read, since it has
            already read the input to confirm data can be produced.
        """
        algorithm = self._algorithm
        input_channels = options.inchannels or \
                algorithm.get_input_channels()
        output_channels = options.outchannels or \
                algorithm.get_output_channels()
        next_starttime = algorithm.get_next_starttime()
        starttime = next_starttime or options.starttime
        endtime = options.endtime
        # input
        timeseries = input_timeseries or self._get_input_timeseries(
                observatory=options.observatory,
                starttime=starttime,
                endtime=endtime,
                channels=input_channels)
        if timeseries.count() == 0:
            # no data to process
            return
        # pre-process
        if next_starttime and options.realtime:
            # when running a stateful algorithms with the realtime option
            # pad/trim timeseries to the interval:
            # [next_starttime, max(timeseries.endtime, now-options.realtime)]
            input_start, input_end = \
                    TimeseriesUtility.get_stream_start_end_times(
                            timeseries, without_gaps=True)
            realtime_gap = endtime - options.realtime
            if input_end < realtime_gap:
                input_end = realtime_gap
            # pad to the start of the "realtime gap"
            TimeseriesUtility.pad_timeseries(timeseries,
                    next_starttime, input_end)
        # process
        if options.rename_input_channel:
            timeseries = self._rename_channels(
                    timeseries=timeseries,
                    renames=options.rename_input_channel)
        processed = algorithm.process(timeseries)
        # trim if --no-trim is not set
        if not options.no_trim:
            processed.trim(starttime=starttime,
                    endtime=endtime)
        if options.rename_output_channel:
            processed = self._rename_channels(
                    timeseries=processed,
                    renames=options.rename_output_channel)
        # output
        self._outputFactory.put_timeseries(
                timeseries=processed,
                starttime=starttime,
                endtime=endtime,
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
        if algorithm.get_next_starttime() is not None:
            raise AlgorithmException(
                    'Stateful algorithms cannot use run_as_update')
        input_channels = options.inchannels or \
                algorithm.get_input_channels()
        output_observatory = options.output_observatory
        output_channels = options.outchannels or \
                algorithm.get_output_channels()
        print('checking gaps', options.starttime, options.endtime,
                output_observatory, output_channels,
                file=sys.stderr)
        # request output to see what has already been generated
        output_timeseries = self._get_output_timeseries(
                observatory=options.output_observatory,
                starttime=options.starttime,
                endtime=options.endtime,
                channels=output_channels)
        if len(output_timeseries) > 0:
            # find gaps in output, so they can be updated
            output_gaps = TimeseriesUtility.get_merged_gaps(
                    TimeseriesUtility.get_stream_gaps(output_timeseries))
        else:
            output_gaps = [[
                options.starttime,
                options.endtime,
                # next sample time not used
                None
            ]]
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
                starttime = options.starttime - interval
                endtime = options.starttime - 1
                options.starttime = starttime
                options.endtime = endtime
                self.run_as_update(options, update_count + 1)
            # fill gap
            options.starttime = output_gap[0]
            options.endtime = output_gap[1]
            print('processing', options.starttime, options.endtime,
                    output_observatory, output_channels,
                    file=sys.stderr)
            self.run(options, input_timeseries)


def get_input_factory(args):
    """Parse input factory arguments.

    Parameters
    ----------
    args : argparse.Namespace
        arguments

    Returns
    -------
    TimeseriesFactory
        input timeseries factory
    """
    input_factory = None
    input_factory_args = None
    input_stream = None

    # standard arguments
    input_factory_args = {}
    input_factory_args['interval'] = args.input_interval or args.interval
    input_factory_args['observatory'] = args.observatory
    input_factory_args['type'] = args.type
    # stream/url arguments
    if args.input_file is not None:
        input_stream = open(args.input_file, 'r')
    elif args.input_stdin:
        input_stream = sys.stdin
    elif args.input_url is not None:
        if '{' in args.input_url:
            input_factory_args['urlInterval'] = args.input_url_interval
            input_factory_args['urlTemplate'] = args.input_url
        else:
            input_stream = BytesIO(Util.read_url(args.input_url))
    input_type = args.input
    if input_type == 'edge':
        input_factory = edge.EdgeFactory(
                host=args.input_host,
                port=args.input_port,
                locationCode=args.locationcode,
                **input_factory_args)
    elif input_type == 'miniseed':
        input_factory = edge.MiniSeedFactory(
                host=args.input_host,
                port=args.input_port,
                locationCode=args.locationcode,
                convert_channels=args.convert_voltbin,
                **input_factory_args)
    elif input_type == 'goes':
        # TODO: deal with other goes arguments
        input_factory = imfv283.GOESIMFV283Factory(
                directory=args.input_goes_directory,
                getdcpmessages=args.input_goes_getdcpmessages,
                password=args.input_goes_password,
                server=args.input_goes_server,
                user=args.input_goes_user,
                **input_factory_args)
    else:
        # stream compatible factories
        if input_type == 'iaga2002':
            input_factory = iaga2002.IAGA2002Factory(**input_factory_args)
        elif input_type == 'imfv122':
            input_factory = imfv122.IMFV122Factory(**input_factory_args)
        elif input_type == 'imfv283':
            input_factory = imfv283.IMFV283Factory(**input_factory_args)
        elif input_type == 'pcdcp':
            input_factory = pcdcp.PCDCPFactory(**input_factory_args)
        # wrap stream
        if input_stream is not None:
            input_factory = StreamTimeseriesFactory(
                    factory=input_factory,
                    stream=input_stream)
    return input_factory


def get_output_factory(args):
    """Parse output factory arguments.

    Parameters
    ----------
    args : argparse.Namespace
        arguments

    Returns
    -------
    TimeseriesFactory
        output timeseries factory
    """
    output_factory = None
    output_factory_args = None
    output_stream = None
    output_url = None

    # standard arguments
    output_factory_args = {}
    output_factory_args['interval'] = args.output_interval or args.interval
    output_factory_args['observatory'] = args.output_observatory
    output_factory_args['type'] = args.type
    # stream/url arguments
    if args.output_file is not None:
        output_stream = open(args.output_file, 'wb')
    elif args.output_stdout:
        try:
            # python 3
            output_stream = sys.stdout.buffer
        except AttributeError:
            # python 2
            output_stream = sys.stdout
    elif args.output_url is not None:
        output_url = args.output_url
        output_factory_args['urlInterval'] = args.output_url_interval
        output_factory_args['urlTemplate'] = output_url

    output_type = args.output
    if output_type == 'edge':
        # TODO: deal with other edge arguments
        locationcode = args.outlocationcode or args.locationcode or None
        output_factory = edge.EdgeFactory(
                host=args.output_host,
                port=args.output_read_port,
                write_port=args.output_port,
                locationCode=locationcode,
                tag=args.output_edge_tag,
                forceout=args.output_edge_forceout,
                **output_factory_args)
    elif output_type == 'miniseed':
        # TODO: deal with other miniseed arguments
        locationcode = args.outlocationcode or args.locationcode or None
        output_factory = edge.EdgeFactory(
                host=args.output_host,
                port=args.output_read_port,
                write_port=args.output_port,
                locationCode=locationcode,
                **output_factory_args)
    elif output_type == 'plot':
        output_factory = PlotTimeseriesFactory()
    else:
        # stream compatible factories
        if output_type == 'binlog':
            output_factory = binlog.BinLogFactory(**output_factory_args)
        elif output_type == 'iaga2002':
            output_factory = iaga2002.IAGA2002Factory(**output_factory_args)
        elif output_type == 'imfjson':
            output_factory = imfjson.IMFJSONFactory(**output_factory_args)
        elif output_type == 'pcdcp':
            output_factory = pcdcp.PCDCPFactory(**output_factory_args)
        elif output_type == 'temperature':
            output_factory = temperature.TEMPFactory(**output_factory_args)
        elif output_type == 'vbf':
            output_factory = vbf.VBFFactory(**output_factory_args)
        # wrap stream
        if output_stream is not None:
            output_factory = StreamTimeseriesFactory(
                    factory=output_factory,
                    stream=output_stream)
    return output_factory


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

    # only try to parse deprecated arguments if they've been enabled
    if args.enable_deprecated_arguments:
        parse_deprecated_arguments(args)

    # make sure observatory is a tuple
    if isinstance(args.observatory, (str, unicode)):
        args.observatory = (args.observatory,)

    if args.output_observatory is None:
        args.output_observatory = args.observatory
    elif args.observatory_foreach:
        raise Exception("Cannot combine" +
             " --output-observatory and --observatory-foreach")

    if args.output_stdout and args.update:
        raise Exception("Cannot combine" +
            " --output-stdout and --update")

    # translate realtime into start/end times
    if args.realtime:
        if args.realtime is True:
            # convert interval to number of seconds
            if args.interval == 'minute':
                args.realtime = 3600
            else:
                args.realtime = 600
        # calculate endtime/starttime
        now = UTCDateTime()
        args.endtime = UTCDateTime(now.year, now.month, now.day,
                now.hour, now.minute)
        args.starttime = args.endtime - args.realtime

    if args.observatory_foreach:
        observatory = args.observatory
        observatory_exception = None
        for obs in observatory:
            args.observatory = (obs,)
            args.output_observatory = (obs,)
            try:
                _main(args)
            except Exception as e:
                print("Exception processing observatory {}".format(obs),
                        str(e),
                        file=sys.stderr)
        if observatory_exception:
            print("Exceptions occurred during processing", file=sys.stderr)
            sys.exit(1)

    else:
        _main(args)


def _main(args):
    """Actual main method logic, called by main

    Parameters
    ----------
    args : argparse.Namespace
        command line arguments
    """
    # create controller
    input_factory = get_input_factory(args)
    output_factory = get_output_factory(args)
    algorithm = algorithms[args.algorithm]()
    algorithm.configure(args)
    controller = Controller(input_factory, output_factory, algorithm)

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
        description="""
            Read, optionally process, and Write Geomag Timeseries data.
            Use @ to read arguments from a file.""",
        fromfile_prefix_chars='@',)

    # Input group
    input_group = parser.add_argument_group('Input', 'How data is read.')

    input_type_group = input_group.add_mutually_exclusive_group(required=True)
    input_type_group.add_argument('--input',
            choices=(
                'edge',
                'goes',
                'iaga2002',
                'imfv122',
                'imfv283',
                'miniseed',
                'pcdcp'
            ),
            default='edge',
            help='Input format (Default "edge")')

    input_group.add_argument('--input-file',
            help='Read from specified file',
            metavar='FILE')
    input_group.add_argument('--input-host',
            default='cwbpub.cr.usgs.gov',
            help='Hostname or IP address (Default "cwbpub.cr.usgs.gov")',
            metavar='HOST')
    input_group.add_argument('--input-interval',
        default=None,
        choices=['day', 'hour', 'minute', 'second', 'tenhertz'],
        help="Default same as --interval",
        metavar='INTERVAL')
    input_group.add_argument('--input-port',
            default=2060,
            help='Port number (Default 2060)',
            metavar='PORT',
            type=int)
    input_group.add_argument('--input-stdin',
            action='store_true',
            default=False,
            help='Read from standard input')
    input_group.add_argument('--input-url',
            help='Read from a url or url pattern.',
            metavar='URL')
    input_group.add_argument('--input-url-interval',
            default=86400,
            help="""
                Seconds of data each url request should return
                (default 86400) used to map requests across multiple files
                or make multiple requests for chunks of data.
                """,
            metavar='N',
            type=int)

    input_group.add_argument('--inchannels',
            nargs='*',
            help='Channels H, E, Z, etc',
            metavar='CHANNEL')
    input_group.add_argument('--interval',
            default='minute',
            choices=['day', 'hour', 'minute', 'second', 'tenhertz'],
            help='Data interval, default "minute"',
            metavar='INTERVAL')
    input_group.add_argument('--locationcode',
            help="""
                Use explicit location code, e.g. "R0", "R1",
                instead of "--type"
                """,
            metavar='CODE',
            type=edge.LocationCode)
    input_group.add_argument('--observatory',
            default=(None,),
            help="""
                Observatory code ie BOU, CMO, etc.
                CAUTION: Using multiple observatories is not
                recommended in most cases; especially with
                single observatory formats like IAGA and PCDCP.
                """,
            metavar='OBS',
            nargs='*',
            type=str,
            required=True)
    input_group.add_argument('--observatory-foreach',
            action='store_true',
            default=False,
            help='When specifying multiple observatories, process'
                    ' each observatory separately')
    input_group.add_argument('--rename-input-channel',
            action='append',
            help="""
                Rename an input channel after it is read,
                before it is processed
                """,
            metavar=('FROM', 'TO'),
            nargs=2)
    input_group.add_argument('--type',
            default='variation',
            choices=['variation',
                     'reported',
                     'provisional',
                     'adjusted',
                     'quasi-definitive',
                     'definitive'],
            help='Data type, default "variation"')
    # time range
    input_group.add_argument('--starttime',
            type=UTCDateTime,
            default=None,
            help='UTC date time YYYY-MM-DD HH:MM:SS',
            metavar='ISO8601')
    input_group.add_argument('--endtime',
            type=UTCDateTime,
            default=None,
            help='UTC date time YYYY-MM-DD HH:MM:SS',
            metavar='ISO8601')
    input_group.add_argument('--realtime',
            default=False,
            const=True,
            help="""
                Run the last N seconds.
                Default 3600 (last hour) when interval is minute,
                Default 600 (last 10 minutes) otherwise.
                """,
            metavar='N',
            nargs='?',
            type=int)

    # conversion from bins/volts to nT
    input_group.add_argument('--convert-voltbin',
            nargs='*',
            default=None,
            metavar='CHANNEL',
            help="""
                Convert channels from bins/volts to nT.
                Example: "
                    --inchannels U_Bin U_Volt
                    --interval tenhertz
                    --type variation
                    --convert-voltbin U
                    --outchannels U
                    "
                """)

    # Output group
    output_group = parser.add_argument_group('Output', 'How data is written.')
    output_type_group = output_group.add_mutually_exclusive_group(
            required=True)

    # output arguments
    output_type_group.add_argument('--output',
            choices=(
                'binlog',
                'edge',
                'iaga2002',
                'imfjson',
                'miniseed',
                'pcdcp',
                'plot',
                'temperature',
                'vbf'
            ),
            # TODO: set default to 'iaga2002'
            help='Output format')

    output_group.add_argument('--outchannels',
            nargs='*',
            default=None,
            help='Defaults to --inchannels',
            metavar='CHANNEL')
    output_group.add_argument('--output-file',
            help='Write to specified file',
            metavar='FILE')
    output_group.add_argument('--output-host',
            default='cwbpub.cr.usgs.gov',
            help='Write to specified host',
            metavar='HOST')
    output_group.add_argument('--output-interval',
            default=None,
            choices=['day', 'hour', 'minute', 'second', 'tenhertz'],
            help="Default same as --interval",
            metavar='INTERVAL')
    output_group.add_argument('--output-observatory',
            default=None,
            help='Defaults to value of --observatory argument.',
            metavar='OBS',
            nargs='*',
            type=str)
    output_group.add_argument('--output-port',
            default=7981,
            help='Write to specified port',
            metavar='PORT',
            type=int)
    output_group.add_argument('--output-read-port',
            default=2060,
            help='Read from specified port',
            metavar='PORT',
            type=int)
    output_group.add_argument('--output-stdout',
            action='store_true',
            default=False,
            help='Write to standard output')
    output_group.add_argument('--output-url',
            help='Write to a file:// url pattern',
            metavar='URL')
    output_group.add_argument('--output-url-interval',
            default=86400,
            help='Output interval in seconds',
            metavar='INTERVAL',
            type=int)
    output_group.add_argument('--rename-output-channel',
            action='append',
            help='Rename an output channel before it is written',
            metavar=('FROM', 'TO'),
            nargs=2)
    output_group.add_argument('--outlocationcode',
            help='Defaults to --locationcode',
            metavar='CODE',
            type=edge.LocationCode)
    output_group.add_argument('--output-edge-forceout',
            action='store_true',
            default=False,
            help='Used when writing to EDGE, to close miniseed immediately.')
    output_group.add_argument('--output-edge-tag',
            default='GEOMAG',
            help='Used when writing to EDGE, to identify source of data.',
            metavar='TAG')

    # Processing group
    processing_group = parser.add_argument_group(
            'Processing',
            'How data is processed.')
    processing_group.add_argument('--algorithm',
            choices=[k for k in algorithms],
            default='identity',
            help='Default is "identity", which skips processing')
    for k in algorithms:
        algorithms[k].add_arguments(processing_group)
    processing_group.add_argument('--update',
            action='store_true',
            default=False,
            help="""
                Check for gaps in output,
                and merge new data into existing.
                """)
    processing_group.add_argument('--update-limit',
            type=int,
            default=0,
            help="""
                Update mode checks for gaps and will step backwards
                to gap fill, if the start of the current interval is a gap,
                when limit is set to more than 0.
                """,
            metavar='N')
    processing_group.add_argument('--no-trim',
            action='store_true',
            default=False,
            help='Ensures output data will not be trimmed down')

    # GOES parameters
    goes_group = parser.add_argument_group(
            'GOES parameters',
            'Used to configure "--input goes"')
    goes_group.add_argument('--input-goes-directory',
            default='.',
            help='Directory for support files for goes input of imfv283 data',
            metavar='PATH')
    goes_group.add_argument('--input-goes-getdcpmessages',
            default='',
            help='Location of getDcpMessages.',
            metavar='PATH')
    goes_group.add_argument('--input-goes-password',
            default='',
            help='Password for goes user',
            metavar='PASSWORD')
    goes_group.add_argument('--input-goes-server',
            nargs='*',
            help='The server name(s) to retrieve the GOES data from',
            metavar='HOST')
    goes_group.add_argument('--input-goes-user',
            default='GEOMAG',
            help='The user name to use to retrieve data from GOES',
            metavar='USER')

    # still allow deprecated arguments for now, but hide behind opt in flag
    deprecated = parser.add_argument_group('Deprecated')
    deprecated.add_argument('--enable-deprecated-arguments',
            action='store_true',
            default=False,
            help="enable support for deprecated arguments")
    # check for this argument before adding deprecated args to usage
    if '--enable-deprecated-arguments' in args:
        add_deprecated_args(deprecated, input_type_group, output_type_group)

    deprecated.add_argument('--volt-conversion',
            default=100.0,
            metavar='NT',
            help='(Deprecated, Unused) Conversion factor (nT/V) for volts')
    deprecated.add_argument('--bin-conversion',
            default=500.0,
            metavar='NT',
            help='(Deprecated, Unused) Conversion factor (nT/bin) for bins')

    return parser.parse_args(args)


def add_deprecated_args(parser, input_group, output_group):
    print('WARNING: you are enabling deprecated arguments,' +
            ' please update your usage', file=sys.stderr)

    # argument options for inputs and outputs,
    # replaced with less TYPE specific options
    parser.add_argument('--input-edge-port',
            type=int,
            default=2060,
            help='(Deprecated) \
                Use "--input-port".',
            metavar='PORT')
    parser.add_argument('--output-edge-port',
            type=int,
            dest='edge_write_port',
            default=7981,
            help='(Deprecated) \
                Use "--output-port".',
            metavar='PORT')
    parser.add_argument('--output-edge-cwb-port',
            type=int,
            dest='edge_write_port',
            default=7981,
            help='(Deprecated) \
                Use "--output miniseed" and "--output-port PORT".',
            metavar='PORT')
    parser.add_argument('--output-edge-read-port',
            type=int,
            default=2060,
            help='(Deprecated) \
                Use "--output-read-port".',
            metavar='PORT')

    # input arguments (generally use "--input TYPE")
    input_group.add_argument('--input-edge',
            help='(Deprecated) \
                Use "--input edge" and "--input-host HOST".',
            metavar='HOST')
    input_group.add_argument('--input-iaga-file',
            help='(Deprecated) \
                Use "--input iaga2002" and "--input-file FILE".',
            metavar='FILE')
    input_group.add_argument('--input-iaga-stdin',
            action='store_true',
            default=False,
            help='(Deprecated) \
                Use "--input iaga2002" and "--input-stdin".')
    input_group.add_argument('--input-iaga-url',
            help='(Deprecated) \
                Use "--input iaga2002" and "--input-url URL".',
            metavar='URL')
    input_group.add_argument('--input-imfv283-file',
            help='(Deprecated) \
                Use "--input imfv283" and "--input-file FILE".',
            metavar='FILE')
    input_group.add_argument('--input-imfv283-stdin',
            action='store_true',
            default=False,
            help='(Deprecated) \
                Use "--input imfv283" and "--input-stdin"')
    input_group.add_argument('--input-imfv283-url',
            help='(Deprecated) \
                Use "--input iaga2002" and "--input-url URL".',
            metavar='URL')
    input_group.add_argument('--input-imfv283-goes',
            action='store_true',
            default=False,
            help='(Deprecated) \
                Use "--input goes".')
    input_group.add_argument('--input-pcdcp-file',
            help='(Deprecated) \
                Use "--input pcdcp" and "--input-file FILE".',
            metavar='FILE')
    input_group.add_argument('--input-pcdcp-stdin',
            action='store_true',
            default=False,
            help='(Deprecated) \
                Use "--input pcddp" and "--input-stdin".')
    input_group.add_argument('--input-pcdcp-url',
            help='(Deprecated) \
                Use "--input pcdcp" and "--input-url URL".',
            metavar='URL')

    # output arguments (generally use "--output TYPE")
    output_group.add_argument('--output-iaga-file',
            help='(Deprecated) \
                Use "--output iaga2002" and "--output-file FILE".',
            metavar='FILE')
    output_group.add_argument('--output-iaga-stdout',
            action='store_true', default=False,
            help='(Deprecated) \
                Use "--output iaga2002" and "--output-stdout".')
    output_group.add_argument('--output-iaga-url',
            help='(Deprecated) \
                Use "--output iaga2002" and "--output-url URL".',
            metavar='URL')
    output_group.add_argument('--output-pcdcp-file',
            help='(Deprecated) \
                Use "--output pcdcp" and "--output-file FILE".',
            metavar='FILE')
    output_group.add_argument('--output-pcdcp-stdout',
            action='store_true', default=False,
            help='(Deprecated) \
                Use "--output pcdcp" and "--output-stdout".')
    output_group.add_argument('--output-pcdcp-url',
            help='(Deprecated) \
                Use "--output pcdcp" and "--output-url URL".',
            metavar='URL')
    output_group.add_argument('--output-edge',
            help='(Deprecated) \
                Use "--output edge" and "--output-host HOST".',
            metavar='HOST')
    output_group.add_argument('--output-plot',
            action='store_true',
            default=False,
            help='(Deprecated) \
                Use "--output plot".')


def parse_deprecated_arguments(args):
    # TODO: remove argument mapping in future version
    # map legacy input arguments
    usingDeprecated = False
    if args.input_edge is not None:
        args.input = 'edge'
        args.input_host = args.input_edge
        args.input_port = args.input_edge_port
        usingDeprecated = True
    elif args.input_iaga_file is not None:
        args.input = 'iaga2002'
        args.input_file = args.input_iaga_file
        usingDeprecated = True
    elif args.input_iaga_stdin:
        args.input = 'iaga2002'
        args.input_stdin = True
        usingDeprecated = True
    elif args.input_iaga_url is not None:
        args.input = 'iaga2002'
        args.input_url = args.input_iaga_url
        usingDeprecated = True
    elif args.input_imfv283_file is not None:
        args.input = 'imfv283'
        args.input_file = args.input_imfv283_file
        usingDeprecated = True
    elif args.input_imfv283_url is not None:
        args.input = 'imfv283'
        args.input_url = args.input_imfv283_url
        usingDeprecated = True
    elif args.input_imfv283_goes:
        args.input = 'goes'
        usingDeprecated = True
    # map legacy output arguments
    if args.output_edge is not None:
        args.output = 'edge'
        args.output_host = args.output_edge
        args.output_port = args.edge_write_port
        usingDeprecated = True
    elif args.output_iaga_file is not None:
        args.output = 'iaga2002'
        args.output_file = args.output_iaga_file
        usingDeprecated = True
    elif args.output_iaga_stdout:
        args.output = 'iaga2002'
        args.output_stdout = True
        usingDeprecated = True
    elif args.output_iaga_url is not None:
        args.output = 'iaga2002'
        args.output_url = args.output_iaga_url
        usingDeprecated = True
    elif args.output_pcdcp_file is not None:
        args.output = 'pcdcp'
        args.output_file = args.output_pcdcp_file
        usingDeprecated = True
    elif args.output_pcdcp_stdout:
        args.output = 'pcdcp'
        args.output_stdout = True
        usingDeprecated = True
    elif args.output_pcdcp_url is not None:
        args.output = 'pcdcp'
        args.output_url = args.output_pcdcp_url
        usingDeprecated = True
    elif args.output_plot:
        args.output = 'plot'
        usingDeprecated = True

    if usingDeprecated:
        print('WARNING: you are using deprecated arguments,' +
              ' please update your usage', file=sys.stderr)
