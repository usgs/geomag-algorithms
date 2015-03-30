"""Algorithm that converts from one geomagnetic coordinate system to a
    related coordinate system.

"""

from Algorithm import Algorithm
import StreamConverter as StreamConverter

# List of channels by geomagnetic observatory orientation.
# geo represents a geographic north/south orientation
# mag represents the (calculated)instantaneous mangnetic north orientation
# obs represents the sensor orientation aligned close to the mag orientation
# obsd is the same as obs,  but with D(declination) instead of E (e/w vector)
CHANNELS = {
    'geo': ['X', 'Y', 'Z', 'F'],
    'mag': ['H', 'D', 'Z', 'F'],
    'obs': ['H', 'E', 'Z', 'F'],
    'obsd': ['H', 'D', 'Z', 'F']
}


class XYZAlgorithm(Algorithm):
    """Algorithm for converting data,  probably inapproprately named XYZ.

    Parameters
    ----------
    informat: str
        the code that represents the incoming data form that the Algorithm
        will be converting from.
    outformat: str
        the code that represents what form the incoming data will
        be converting to.
    """

    def __init__(self, informat=None, outformat=None):
        Algorithm.__init__(self)
        self.informat = informat
        self.outformat = outformat

    def check_stream(self, timeseries, channels):
        """checks an stream to make certain all the required channels
            exist.

        Parameters
        ----------
        timeseries: obspy.core.Stream
            stream to be checked.
        channels: array_like
            channels that are expected in stream.
        """
        for channel in channels:
            if len(timeseries.select(channel=channel)) == 0:
                print 'Channel %s not found in input' % channel
                return False
        return True

    def get_input_channels(self):
        """Get input channels

        Returns
        -------
        array_like
            list of channels the algorithm needs to operate.
        """
        return CHANNELS[self.informat]

    def get_output_channels(self):
        """Get output channels

        Returns
        -------
        array_like
            list of channels the algorithm will be returning.
        """
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
