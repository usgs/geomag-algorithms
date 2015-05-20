#! /usr/bin/env python

import argparse
import sys

# ensure geomag is on the path before importing
try:
    import geomagio  # noqa (tells linter to ignore this line.)
except:
    from os import path
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, '..')))

import geomagio.iaga2002 as iaga2002
import geomagio.edge as edge
import geomagio.pcdcp as pcdcp
from geomagio.Algorithm import Algorithm
from geomagio.XYZAlgorithm import XYZAlgorithm
from geomagio.Controller import Controller
from obspy.core.utcdatetime import UTCDateTime


def main():
    """command line factory for geomag algorithms

    Inputs
    ------
    use geomag.py --help to see inputs

    Notes
    -----
    parses command line options using argparse, then calls the controller
    with instantiated I/O factories, and algorithm(s)
    """

    args = parse_args()

    # Input Factory
    if args.input_edge is not None:
        inputfactory = edge.EdgeFactory(
                host=args.input_edge[0],
                port=int(args.input_edge[1]),
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
                host=args.output_edge[0],
                port=int(args.output_edge[1]),
                observatory=args.observatory,
                type=args.type,
                interval=args.interval,
                locationCode=locationcode)
    else:
            print >> sys.stderr, "Missing required output directive"

    if args.xyz is not None:
        algorithm = XYZAlgorithm(informat=args.xyz[0],
                outformat=args.xyz[1])
    else:
        algorithm = Algorithm(inchannels=args.inchannels,
                outchannels=args.outchannels)

    # TODO check for unused arguments.

    controller = Controller(inputfactory, outputfactory, algorithm)

    controller.run(UTCDateTime(args.starttime), UTCDateTime(args.endtime))


def parse_args():
    """parse input arguments

    Returns
    -------
    argparse.Namespace
        dictionary like object containing arguments.
    """
    parser = argparse.ArgumentParser(
        description='Use @ to read commands from a file.',
        fromfile_prefix_chars='@',)

    parser.add_argument('--starttime', default=UTCDateTime(),
            help='UTC date YYYY-MM-DD HH:MM:SS')
    parser.add_argument('--endtime', default=UTCDateTime(),
            help='UTC date YYYY-MM-DD HH:MM:SS')

    parser.add_argument('--observatory',
            help='Observatory code ie BOU, CMO, etc')
    parser.add_argument('--inchannels', nargs='*',
            help='Channels H, E, Z, etc')
    parser.add_argument('--outchannels', nargs='*',
            help='Channels H, E, Z, etc')
    parser.add_argument('--type', default='variation',
            choices=['variation', 'quasi-definitive', 'definitive'])
    parser.add_argument('--locationcode',
            choices=['R0', 'R1', 'RM', 'Q0', 'D0', 'C0'])
    parser.add_argument('--outlocationcode',
            choices=['R0', 'R1', 'RM', 'Q0', 'D0', 'C0'])
    parser.add_argument('--interval', default='minute',
            choices=['minute', 'second'])

    # Input group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input-edge', nargs=2,
            metavar=('HOST', 'PORT'),
            help='Requires Host IP # and Port #.')
    input_group.add_argument('--input-iaga-file',
            help='Reads from the specified file.')
    input_group.add_argument('--input-iaga-magweb',
            action='store_true', default=False,
            help='Indicates iaga2002 files will be read from \
            http://magweb.cr.usgs.gov/data/magnetometer/')
    input_group.add_argument('--input-iaga-stdin',
            action='store_true', default=False,
            help='Pass in an iaga file using redirection from stdin.')
    input_group.add_argument('--input-iaga-url',
            help='Example: file://./%%(obs)s%%(ymd)s%%(t)s%%(i)s.%%(i)s')
    input_group.add_argument('--input-pcdcp-file',
            help='Reads from the specified file.')
    input_group.add_argument('--input-pcdcp-stdin',
            action='store_true', default=False,
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
    output_group.add_argument('--output-edge', nargs=2,
            metavar=('HOST', 'PORT'),
            help='Requires Host IP # and Port #')

    # Algorithms group
    algorithm_group = parser.add_mutually_exclusive_group()
    algorithm_group.add_argument('--xyz', nargs=2,
            choices=['geo', 'mag', 'obs', 'obsd'],
            help='Enter the geomagnetic orientation(s) you want to read from' +
                    ' and to respectfully.')

    return parser.parse_args()


if __name__ == '__main__':
    main()
