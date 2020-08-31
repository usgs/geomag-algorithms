"""Algorithm that converts from one geomagnetic coordinate system to a
    related coordinate system.

"""
from __future__ import absolute_import

from .Algorithm import Algorithm
from .AlgorithmException import AlgorithmException
from .. import StreamConverter

# List of channels by geomagnetic observatory orientation.
# geo represents a geographic north/south orientation
# mag represents the (calculated)instantaneous mangnetic north orientation
# obs represents the sensor orientation aligned close to the mag orientation
# obsd is the same as obs,  but with D(declination) instead of E (e/w vector)
CHANNELS = {
    "geo": ["X", "Y", "Z", "F"],
    "mag": ["H", "D", "Z", "F"],
    "obs": ["H", "E", "Z", "F"],
    "obsd": ["H", "D", "Z", "F"],
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

    def __init__(self, informat="obs", outformat="geo"):
        Algorithm.__init__(
            self, inchannels=CHANNELS[informat], outchannels=CHANNELS[outformat]
        )
        self._informat = informat
        self._outformat = outformat

    def check_stream(self, timeseries):
        """checks an stream to make certain all the required channels
            exist.

        Parameters
        ----------
        timeseries: obspy.core.Stream
            stream to be checked.
        channels: array_like
            channels that are expected in stream.
        """
        for channel in self.get_required_channels():
            if len(timeseries.select(channel=channel)) == 0:
                raise AlgorithmException("Channel %s not found in input" % channel)

    def get_required_channels(self):
        """Only the first two channels are required
        for the XYZAlgorithm
        """
        return self._inchannels[:2]

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
        self.check_stream(timeseries)
        out_stream = None
        informat = self._informat
        outformat = self._outformat
        if outformat == "geo":
            if informat == "geo":
                out_stream = timeseries
            elif informat == "mag":
                out_stream = StreamConverter.get_geo_from_mag(timeseries)
            elif informat == "obs" or informat == "obsd":
                out_stream = StreamConverter.get_geo_from_obs(timeseries)
        elif outformat == "mag":
            if informat == "geo":
                out_stream = StreamConverter.get_mag_from_geo(timeseries)
            elif informat == "mag":
                out_stream = timeseries
            elif informat == "obs" or informat == "obsd":
                out_stream = StreamConverter.get_mag_from_obs(timeseries)
        elif outformat == "obs":
            if informat == "geo":
                out_stream = StreamConverter.get_obs_from_geo(timeseries)
            elif informat == "mag":
                out_stream = StreamConverter.get_obs_from_mag(timeseries)
            elif informat == "obs" or informat == "obsd":
                out_stream = StreamConverter.get_obs_from_obs(
                    timeseries, include_e=True
                )
        elif outformat == "obsd":
            if informat == "geo":
                out_stream = StreamConverter.get_obs_from_geo(
                    timeseries, include_d=True
                )
            elif informat == "mag":
                out_stream = StreamConverter.get_obs_from_mag(
                    timeseries, include_d=True
                )
            elif informat == "obs" or informat == "obsd":
                out_stream = StreamConverter.get_obs_from_obs(
                    timeseries, include_d=True
                )
        return out_stream

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.

        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """
        parser.add_argument(
            "--xyz-from",
            choices=["geo", "mag", "obs", "obsd"],
            default="obs",
            help="Geomagnetic orientation to read from",
        )
        parser.add_argument(
            "--xyz-to",
            choices=["geo", "mag", "obs", "obsd"],
            default="geo",
            help="Geomagnetic orientation to convert to",
        )

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.

        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        self._informat = arguments.xyz_from
        self._outformat = arguments.xyz_to
        self._inchannels = CHANNELS[self._informat]
        self._outchannels = CHANNELS[self._outformat]
