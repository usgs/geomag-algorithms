#! /usr/bin/env python

import argparse
from os import path
import os
#ensure geomag is on the path before importing
script_dir = path.dirname(path.abspath(__file__))
if __file__ != 'main.py':
    import sys
    sys.path.append(path.normpath(path.join(script_dir, '..')))

import geomagio.iaga2002 as iaga2002
from geomagio.iaga2002.IAGA2002Factory import read_url
import geomagio.StreamConverter as StreamConverter

# static containing the standard output types for iaga2002 files.
CHANNELS = {
    'geo': ['X', 'Y', 'Z', 'F'],
    'mag': ['H', 'D', 'Z', 'F'],
    'obs': ['H', 'E', 'Z', 'F']
    }

def get_out_channels(args):
    """Returns the output channels based on the flags.

    Parameteers
    -----------
    args: namespace/dictionary
        outformat: string
            indicates the desired output format
        d_out: boolean
            indicates if the 'observatory' ouput format should include d
                instead of e

    Returns
    -------
    array of strings
        array of output channels
    """
    format = args.outformat
    # obs is only HEZF if --d_out flag is not set.
    # Otherwise it's HDZF same as mag
    if format == 'obs' and args.d_out == True:
        format = 'mag'
    return CHANNELS[format]

def convert_stream(args, timeseries):
    """converts a timeseries stream into a different coordinate system

    Parameters
    ----------
    args: namespace/dictionary
        outformat: string
            indicates the output coordinate system.
        informat: string
            indicates the input coordinate system.
    out_stream: obspy.core.Stream
        new stream object containing the converted coordinates.
    """
    out_stream = None
    if args.outformat == 'geo' and args.informat == 'mag':
        out_stream = StreamConverter.get_geo_from_mag(timeseries)

    if args.outformat == 'geo' and args.informat == 'obs':
        out_stream = StreamConverter.get_geo_from_obs(timeseries)

    if args.outformat == 'mag' and args.informat == 'obs':
        out_stream = StreamConverter.get_mag_from_obs(timeseries)

    if args.outformat == 'mag' and args.informat == 'geo':
        out_stream = StreamConverter.get_mag_from_geo(timeseries)

    if args.outformat == 'obs' and args.informat == 'mag':
        out_stream = StreamConverter.get_obs_from_mag(timeseries)

    if args.outformat == 'obs' and args.informat == 'geo':
        out_stream = StreamConverter.get_obs_from_geo(timeseries, args.d_out)

    if args.outformat == 'obs' and args.informat == 'obs':
        out_stream = StreamConverter.get_obs_from_obs(timeseries,
          True, args.d_out)

    return out_stream



def main():
    """Converts iaga2002 files from one coordinate system to another.

    Inputs
    ------
    informat: string
        The input format/coordinate system of the input file.
            geo: geographic coordinate system (xyzf)
            mag: magnetic north coordinate system (hdzf)
            obs: observatory coordinate system (hezf or hdzf)
    outformat: string
        The ouput format/coordinate system of the output file.
            geo: geographic coordinate system (xyzf)
            mag: magnetic north coordinate system (hdzf)
            obs: observatory coordinate system (hezf or hdzf)
    infile: string
        the filename of the Iaga2002 file to be read from
    outfile: string
        the filename of a new Iaga2002 file to be read to
    d_out: boolean
        a flag indicating whether the output for the observatory coordinate
            system should have the e coordinate instead of d.
    """
    parser = argparse.ArgumentParser(
        description='Use @ to read commands from a file.',
        fromfile_prefix_chars='@')

    parser.add_argument('--informat', choices=['geo', 'mag', 'obs'],
        default='obs')
    parser.add_argument('--outformat', choices=['geo', 'mag', 'obs'],
        default='geo')
    parser.add_argument('--infile', help='iaga2002 input file')
    parser.add_argument('--outfile', help='iaga2002 out file')
    parser.add_argument('--d_out',
        help='output D in the IAGA2002 file instead of E for obs coordinates',
        type=bool,
        default=False)

    args = parser.parse_args()

    iagaFile = ''
    if args.infile != None:
        file_name = 'file://' + path.join(os.getcwd(), args.infile)
        iagaFile = read_url(file_name)
    else:
        for line in sys.stdin:
          iagaFile += line

    factory = iaga2002.IAGA2002Factory(None)

    timeseries = factory.parse_file(iagaFile)
    out_stream = convert_stream(args, timeseries)
    channels = get_out_channels(args)
    print channels
    if args.outfile != None:
        fh = open(args.outfile, 'w')
    else:
        fh = sys.stdout
    iaga2002.IAGA2002Writer().write(fh, out_stream, channels)


if __name__ == '__main__':
    main()
