"""Algorithm that converts from one geomagnetic coordinate system to a
    related coordinate system.

"""

from Algorithm import Algorithm
from AlgorithmException import AlgorithmException
import StreamConverter as StreamConverter

# List of channels by geomagnetic observatory orientation.
# geo represents a geographic north/south orientation
# mag represents the (calculated)instantaneous mangnetic north orientation
# obs represents the sensor orientation aligned close to the mag orientation
# obsd is the same as obs,  but with D(declination) instead of E (e/w vector)
CHANNELS = {
    'geo': ['X', 'Y', 'Z', 'F'],
    'obs': ['H', 'E', 'Z', 'F'],
    'obsd': ['H', 'D', 'Z', 'F']
}


class DeltaFAlgorithm(Algorithm):
    """Algorithm for getting Delta F.

    Parameters
    ----------
    informat: str
        the code that represents the incoming data form that the Algorithm
        will be converting from.
    """

    def __init__(self, informat=None):
        Algorithm.__init__(self, inchannels=CHANNELS[informat],
                outchannels=['G'])
        self.informat = informat

    def check_stream(self, timeseries):
        """checks an stream to make certain all the required channels
            exist.

        Parameters
        ----------
        timeseries: obspy.core.Stream
            stream to be checked.
        """
        for channel in self._inchannels:
            if len(timeseries.select(channel=channel)) == 0:
                raise AlgorithmException(
                    'Channel %s not found in input' % channel)

    def process(self, timeseries):
        """converts a timeseries stream into a different coordinate system

        Parameters
        ----------
        informat: string
            indicates the input coordinate system.

        Returns
        -------
        out_stream: obspy.core.Stream
            new stream object containing the converted coordinates.
        """
        self.check_stream(timeseries)
        out_stream = None

        if self.informat == 'geo':
            out_stream = StreamConverter.get_deltaf_from_geo(timeseries)
        elif self.informat == 'obs' or self.informat == 'obsd':
            out_stream = StreamConverter.get_deltaf_from_obs(timeseries)

        return out_stream
