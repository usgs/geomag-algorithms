"""Controller class for geomag algorithms"""


import argparse
import sys
from obspy.core import UTCDateTime
from Algorithm import Algorithm
import TimeseriesUtility
from TimeseriesFactoryException import TimeseriesFactoryException
from Util import ObjectView

import edge
import iaga2002
import pcdcp

from DeltaFAlgorithm import DeltaFAlgorithm
from XYZAlgorithm import XYZAlgorithm


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
        delta = output_timeseries[0].stats.delta
        # find gaps in output, so they can be updated
        output_gaps = TimeseriesUtility.get_merged_gaps(
                TimeseriesUtility.get_stream_gaps(output_timeseries))
        for output_gap in output_gaps:
            input_start, input_end = algorithm.get_input_interval(
                    start=output_gap[0],
                    end=output_gap[1])
            input_timeseries = self._inputFactory.get_timeseries(
                    starttime=input_start,
                    endtime=input_end,
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
                self.run_as_update(ObjectView({
                    'outchannels': options.outchannels,
                    'starttime': options.starttime - interval - delta,
                    'endtime': options.starttime - delta
                }))
            # fill gap
            self.run(ObjectView({
                'outchannels': options.outchannels,
                'starttime': output_gap[0],
                'endtime': output_gap[1]
            }))

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
                stream=open(args.output_iaga_file, 'w'),
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
                stream=open(args.output_pcdcp_file, 'w'),
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
                tag=args.output_edge_tag)
    else:
            print >> sys.stderr, "Missing required output directive"

    if args.xyz is not None:
        algorithm = XYZAlgorithm(informat=args.xyz[0],
                outformat=args.xyz[1])
    elif args.deltaf is not None:
        algorithm = DeltaFAlgorithm(informat=args.deltaf)
    else:
        # TODO get smarter on inchannels/outchannels since input doesn't always
        # need to use the --inchannels argument, but might (as in iaga2002),
        # get it from the file.
        algorithm = Algorithm(inchannels=args.inchannels,
                outchannels=args.outchannels or args.inchannels)

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
            help='Observatory code ie BOU, CMO, etc')
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
    parser.add_argument('--locationcode',
            choices=['R0', 'R1', 'RM', 'Q0', 'D0', 'C0'])
    parser.add_argument('--outlocationcode',
            choices=['R0', 'R1', 'RM', 'Q0', 'D0', 'C0'])
    parser.add_argument('--interval',
            default='minute',
            choices=['minute', 'second'])
    parser.add_argument('--update',
            action='store_true',
            default=False,
            help='Used to update data')
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
    parser.add_argument('--realtime',
            action='store_true',
            default=False,
            help='Flag to run the last hour if interval is minute' +
                    'or the last 10 minutes if interval is seconds')

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

    # Algorithms group
    algorithm_group = parser.add_mutually_exclusive_group()
    algorithm_group.add_argument('--xyz',
            nargs=2,
            choices=['geo', 'mag', 'obs', 'obsd'],
            help='Enter the geomagnetic orientation(s) you want to read from' +
                    ' and to respectfully.')
    algorithm_group.add_argument('--deltaf',
            choices=['geo', 'obs', 'obsd'],
            help='Enter the geomagnetic orientation you want to read from')

    return parser.parse_args(args)
