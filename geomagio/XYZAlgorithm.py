#! /usr/bin/env python

"""Takes a timeseries stream in,  and returns a converted timeseries stream out

"""

from Algorithm import Algorithm
import StreamConverter as StreamConverter

# static containing the standard output types for iaga2002 files.
CHANNELS = {
    'geo': ['X', 'Y', 'Z', 'F'],
    'mag': ['H', 'D', 'Z', 'F'],
    'obs': ['H', 'E', 'Z', 'F'],
    'obsd': ['H', 'D', 'Z', 'F']
}


class XYZAlgorithm(Algorithm):

    def __init__(self, informat=None, outformat=None):
        Algorithm.__init__(self)
        self.informat = informat
        self.outformat = outformat

    def check_stream(self, timeseries, channels):
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

    def get_input_channels(self):
        return CHANNELS[self.informat]

    def get_output_channels(self):
        return CHANNELS[self.outformat]

    def process(self, timeseries):
        """converts a timeseries stream into a different coordinate system

        Parameters
        ----------
        informat: string
            indicates the input coordinate system.
        outformat: string
            indicates the output coordinate system.
        out_stream: obspy.core.Stream
            new stream object containing the converted coordinates.
        """
        out_stream = None
        if self.outformat == 'geo':
            if self.informat == 'geo':
                out_stream = timeseries
            elif self.informat == 'mag':
                out_stream = StreamConverter.get_geo_from_mag(timeseries)
            elif self.informat == 'obs' or self.informat == 'obsd':
                out_stream = StreamConverter.get_geo_from_obs(timeseries)
        elif self.outformat == 'mag':
            if self.informat == 'geo':
                out_stream = StreamConverter.get_mag_from_geo(timeseries)
            elif self.informat == 'mag':
                out_stream = timeseries
            elif self.informat == 'obs' or self.informat == 'obsd':
                out_stream = StreamConverter.get_mag_from_obs(timeseries)
        elif self.outformat == 'obs':
            if self.informat == 'geo':
                out_stream = StreamConverter.get_obs_from_geo(timeseries)
            elif self.informat == 'mag':
                out_stream = StreamConverter.get_obs_from_mag(timeseries)
            elif self.informat == 'obs' or self.informat == 'obsd':
                out_stream = StreamConverter.get_obs_from_obs(timeseries,
                        include_e=True)
        elif self.outformat == 'obsd':
            if self.informat == 'geo':
                out_stream = StreamConverter.get_obs_from_geo(timeseries,
                        include_d=True)
            elif self.informat == 'mag':
                out_stream = StreamConverter.get_obs_from_mag(timeseries,
                        include_d=True)
            elif self.informat == 'obs' or self.informat == 'obsd':
                out_stream = StreamConverter.get_obs_from_obs(timeseries,
                        include_d=True)
        return out_stream
