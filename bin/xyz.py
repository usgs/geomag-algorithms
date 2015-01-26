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

CHANNELS = {
    'geo': ['X', 'Y', 'Z', 'F'],
    'mag': ['H', 'D', 'Z', 'F'],
    'obs': ['H', 'E', 'Z', 'F']
    }

def get_out_channels(args):
    """
    """
    format = args.outformat
    # obs is only HEZF if --e_out flag is set.  Otherwise it's HDZF same as mag
    if format == 'obs' and args.e_out == False:
        format = 'mag'
    return CHANNELS[format]

def convert_stream(args, timeseries):
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
        out_stream = StreamConverter.get_obs_from_geo(timeseries)

    if args.outformat == 'obs' and args.informat == 'obs':
        out_stream = StreamConverter.get_obs_from_obs(timeseries,
          args.e_out, True)

    return out_stream



def main():
    parser = argparse.ArgumentParser(
        description='Use @ to read commands from a file.',
        fromfile_prefix_chars='@')

    parser.add_argument('--informat', choices=['geo', 'mag', 'obs'],
        default='obs')
    parser.add_argument('--outformat', choices=['geo', 'mag', 'obs'],
        default='geo')
    parser.add_argument('--infile', help='iaga2002 input file')
    parser.add_argument('--outfile', help='iaga2002 out file')
    parser.add_argument('--e_out',
        help='output E in the IAGA2002 file instead of D',
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
    if args.outfile != None:
        fh = open(args.outfile, 'w')
    else:
        fh = sys.stdout
    iaga2002.IAGA2002Writer().write(fh, out_stream, channels)


if __name__ == '__main__':
    main()
