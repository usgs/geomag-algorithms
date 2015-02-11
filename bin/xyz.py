#! /usr/bin/env python

"""Converts iaga2002 files from one coordinate system to another.

    Inputs
    ------
    informat: string
        The input format/coordinate system of the input file.
            geo: geographic coordinate system (xyzf)
            mag: magnetic north coordinate system (hdzf)
            obs: observatory coordinate system (hezf)
            obsd: observatory coordinate system (hdzf)
    outformat: string
        The ouput format/coordinate system of the output file.
            geo: geographic coordinate system (xyzf)
            mag: magnetic north coordinate system (hdzf)
            obs: observatory coordinate system (hezf or hdzf)
    infile: string
        the filename of the Iaga2002 file to be read from
    outfile: string
        the filename of a new Iaga2002 file to be read to
"""

import argparse
import sys
# ensure geomag is on the path before importing
if __file__ != 'xyz.py':
    from os import path
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, '..')))

import geomagio.iaga2002 as iaga2002
import geomagio.StreamConverter as StreamConverter

# static containing the standard output types for iaga2002 files.
CHANNELS = {
    'geo': ['X', 'Y', 'Z', 'F'],
    'mag': ['H', 'D', 'Z', 'F'],
    'obsd': ['H', 'D', 'Z', 'F'],
    'obs': ['H', 'E', 'Z', 'F']
    }

def convert_stream(timeseries, informat, outformat):
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
    if outformat == 'geo':
        if informat == 'obs' or informat == 'obsd':
            out_stream = StreamConverter.get_geo_from_obs(timeseries)
        elif informat == 'mag':
            out_stream = StreamConverter.get_geo_from_mag(timeseries)
    elif outformat == 'mag':
        if informat == 'obs' or informat == 'obsd':
            out_stream = StreamConverter.get_mag_from_obs(timeseries)
        elif informat == 'geo':
            out_stream = StreamConverter.get_mag_from_geo(timeseries)
    elif outformat == 'obs':
        if informat == 'mag':
            out_stream = StreamConverter.get_obs_from_mag(timeseries)
        elif informat == 'geo':
            out_stream = StreamConverter.get_obs_from_geo(timeseries)
        elif informat == 'obs' or informat == 'obsd':
            out_stream = StreamConverter.get_obs_from_obs(timeseries,
                include_e=True)
    elif outformat == 'obsd':
        if informat == 'geo':
            out_stream = StreamConverter.get_obs_from_geo(timeseries,
                    include_d=True)
        elif informat == 'obs':
            out_stream = StreamConverter.get_obs_from_obs(timeseries,
                    include_d=True)

    return out_stream

def check_stream(timeseries, channels):
    """checks an input stream to make certain all the required channels
        exist.

    Parameters
    ----------
    timeseries: obspy.core.Stream
        stream that was read in.
    channels: array
        channels that are expected in stream.
    """
    for channel in channels:
        if len(timeseries.select(channel=channel)) == 0:
            print 'Channel %s not found in input' % channel
            return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Use @ to read commands from a file.',
        fromfile_prefix_chars='@')

    parser.add_argument('--informat', choices=['geo', 'mag', 'obs', 'obsd'],
            required=True)
    parser.add_argument('--outformat', choices=['geo', 'mag', 'obs', 'obsd'],
            required=True)
    parser.add_argument('--infile', help='iaga2002 input file')
    parser.add_argument('--outfile', help='iaga2002 out file')

    args = parser.parse_args()

    iagaFile = ''
    if args.infile != None:
            iagaFile = open(args.infile, 'r').read()
    else:
        print >> sys.stderr, 'Reading iaga2002 format from STDIN'
        iagaFile = sys.stdin.read()

    factory = iaga2002.IAGA2002Factory(None)

    timeseries = factory.parse_string(iagaFile)
    if check_stream(timeseries, CHANNELS[args.informat]) == False:
        sys.exit()
    out_stream = convert_stream(timeseries, args.informat, args.outformat)
    channels = CHANNELS[args.outformat]
    if args.outfile != None:
        fh = open(args.outfile, 'w')
    else:
        fh = sys.stdout
    factory.write_file(fh, out_stream, channels)
    fh.close()


if __name__ == '__main__':
    main()
