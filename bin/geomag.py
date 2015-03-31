#! /usr/bin/env python

import argparse
import sys

# ensure geomag is on the path before importing
try:
    import geomagio  # noqa
except:
    from os import path
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, '..')))

import geomagio.iaga2002 as iaga2002
import geomagio.edge as edge
from geomagio.Algorithm import Algorithm
from geomagio.XYZAlgorithm import XYZAlgorithm
from geomagio.Controller import Controller
from geomagio.iaga2002.IAGA2002Factory import IAGA_FILE_PATTERN
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

    if args.input == 'iaga':
        if args.input_iaga_magweb:
            inputfactory = iaga2002.MagWebFactory(
                    observatory=args.observatory,
                    type=args.type,
                    interval=args.interval)
        elif args.input_iaga_url is not None:
            inputfactory = iaga2002.IAGA2002Factory(
                    urlTemplate=_get_iaga_input_url(args),
                    observatory=args.observatory,
                    type=args.type,
                    interval=args.interval)
        elif args.input_iaga_file is not None or args.input_iaga_stdin:
            if args.input_iaga_file is not None:
                iagaFile = open(args.input_iaga_file, 'r').read()
            else:
                print >> sys.stderr, "Iaga Input waiting for data from stdin"
                iagaFile = sys.stdin.read()
            inputfactory = iaga2002.StreamIAGA2002Factory(
                stream=iagaFile,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
        else:
            print >> sys.stderr, "Iaga Input was missing needed arguments"

    elif args.input == 'edge':
        inputfactory = edge.EdgeFactory(
                host=args.input_edge_host,
                port=args.input_edge_port,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)

    if args.output == 'iaga':
        if args.output_iaga_url is not None:
            outputfactory = iaga2002.IAGA2002Factory(
                    urlTemplate=_get_iaga_output_url(args),
                    observatory=args.observatory,
                    type=args.type,
                    interval=args.interval)
        elif args.output_iaga_file is not None:
            iagaFile = open(args.output_iaga_file, 'w')
            outputfactory = iaga2002.StreamIAGA2002Factory(
                stream=iagaFile,
                observatory=args.observatory,
                type=args.type,
                interval=args.interval)
        elif args.output_iaga_stdout:
            iagaFile = sys.stdout
            outputfactory = iaga2002.StreamIAGA2002Factory(
                    stream=iagaFile,
                    observatory=args.observatory,
                    type=args.type,
                    interval=args.interval)
        else:
            print >> sys.stderr, "Iaga Output was missing needed arguments"

    if args.algorithm == 'xyz':
        algorithm = XYZAlgorithm(args.xyz_informat, args.xyz_outformat)
    else:
        algorithm = Algorithm(channels=args.channels)

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

    parser.add_argument('--input', choices=['iaga', 'edge'],
            help='Input type.', required=True)

    parser.add_argument('--output', choices=['iaga'],
            help='Input type.', required=True)

    parser.add_argument('--starttime', default=UTCDateTime(),
            help='UTC date YYYY-MM-DD HH:MM:SS')
    parser.add_argument('--endtime', default=UTCDateTime(),
            help='UTC date YYYY-MM-DD HH:MM:SS')

    parser.add_argument('--observatory',
            help='Observatory code ie BOU, CMO, etc')
    parser.add_argument('--channels', nargs='*',
            help='Channels H, E, Z, etc')
    parser.add_argument('--type', default='variation',
            choices=['variation', 'quasi-definitive', 'definitive'])
    parser.add_argument('--interval', default='minute',
            choices=['minute', 'second'])

    parser.add_argument('--algorithm', choices='xyz')

    # xyz algorithm arguments
    parser.add_argument('--xyz-informat',
            choices=['geo', 'mag', 'obs', 'obsd'])
    parser.add_argument('--xyz-outformat',
            choices=['geo', 'mag', 'obs', 'obsd'])

    # iaga2002 input arguments
    parser.add_argument('--input-iaga-file',
            help='Iaga2002 filename')
    parser.add_argument('--input-iaga-magweb',
            action="store_true", default=False,
            help='Indicates iaga2002 files will be read from \
            http://magweb.cr.usgs.gov/data/magnetometer/')
    parser.add_argument('--input-iaga-stdin',
            action="store_true", default=False,
            help='Indicates file will be redirected from stdin')
    parser.add_argument('--input-iaga-url',
            help='Url or Directory where Iaga2002 files can be read from')
    parser.add_argument('--input-iaga-urltemplate',
            help='Template for directory matching')
    parser.add_argument('--input-iaga-filetemplate',
            help='Template for iaga filenames')

    parser.add_argument('--output-iaga-url',
            help='Url or Directory where IAGA2002 files should be written to')
    parser.add_argument('--output-iaga-stdout',
            action="store_true", default=False,
            help='Indicates file will be directed to stdout')
    parser.add_argument('--output-iaga-urltemplate',
            help='Template for subdirectories')
    parser.add_argument('--output-iaga-filetemplate',
            help='Template for iaga filenames')
    parser.add_argument('--output-iaga-file',
            help='Output file name for single iaga file.')

    # Edge input arguments
    parser.add_argument('--input-edge-host',
            help='ip address of the edge input server')
    parser.add_argument('--input-edge-port', type=int,
            help='port number of the edge input server')

    return parser.parse_args()


def _get_iaga_input_url(args):
    """get iaga input url

    Parameters
    ----------
    args: argparse.Namespace
        all the arguments passed to geomag.py
        input_iaga_url: string
            the start of the url to read from
        input_iaga_urltemplate: string
            the template for the subdirectories to be read from
        input_iaga_filetemplate:string
            the template for the file

    Returns
    -------
    complete template for the input url
    """
    url = args.input_iaga_url or 'file://./'
    urltemplate = args.input_iaga_urltemplate or ''
    filetemplate = args.input_iaga_filetemplate or IAGA_FILE_PATTERN
    return url + urltemplate + filetemplate


def _get_iaga_output_url(args):
    """get iaga input url

    Parameters
    ----------
    args: argparse.Namespace
        all the arguments passed to geomag.py
        output_iaga_url: string
            the start of the url to read from
        output_iaga_urltemplate: string
            the template for the subdirectories to be read from
        output_iaga_filetemplate:string
            the template for the file

    Returns
    -------
    complete template for the output url
    """
    url = args.output_iaga_url or 'file://./'
    urltemplate = args.output_iaga_urltemplate or ''
    filetemplate = args.output_iaga_filetemplate or IAGA_FILE_PATTERN
    return url + urltemplate + filetemplate

if __name__ == '__main__':
    main()
