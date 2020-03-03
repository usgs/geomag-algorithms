"""Algorithm that creates a deltaf

"""
from __future__ import absolute_import

from .Algorithm import Algorithm
from .AlgorithmException import AlgorithmException
from .. import StreamConverter

# List of channels by geomagnetic observatory orientation.
# geo represents a geographic north/south orientation
# obs represents the sensor orientation aligned close to the mag orientation
# obsd is the same as obs,  but with D(declination) instead of E (e/w vector)
CHANNELS = {
    "geo": ["X", "Y", "Z", "F"],
    "obs": ["H", "E", "Z", "F"],
    "obsd": ["H", "D", "Z", "F"],
}


class DeltaFAlgorithm(Algorithm):
    """Algorithm for getting Delta F.

    Parameters
    ----------
    informat: str
        the code that represents the incoming data form that the Algorithm
        will be converting from.
    """

    def __init__(self, informat="obs"):
        Algorithm.__init__(self, inchannels=CHANNELS[informat], outchannels=["G"])
        self._informat = informat

    def check_stream(self, timeseries):
        """checks a stream to make certain all the required channels
            exist.

        Parameters
        ----------
        timeseries: obspy.core.Stream
            stream to be checked.
        """
        for channel in self._inchannels:
            if len(timeseries.select(channel=channel)) == 0:
                raise AlgorithmException("Channel %s not found in input" % channel)

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
        informat = self._informat
        if informat == "geo":
            out_stream = StreamConverter.get_deltaf_from_geo(timeseries)
        elif informat == "obs" or informat == "obsd":
            out_stream = StreamConverter.get_deltaf_from_obs(timeseries)

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
            "--deltaf-from",
            choices=["geo", "obs", "obsd"],
            default="obs",
            help="Geomagnetic orientation to read from",
        )

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.

        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        self._informat = arguments.deltaf_from
        self._inchannels = CHANNELS[self._informat]
