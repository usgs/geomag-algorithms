"""Algorithm Interface."""

from .. import TimeseriesUtility
import obspy.core


class Algorithm(object):
    """Base class for geomag algorithms

    Parameters
    ----------
    channels: array_like
        the list of channels to be processed.

    Notes
    -----
    An algorithm processes a stream of timeseries to produce new timeseries.
    """

    def __init__(self, inchannels=None, outchannels=None):
        self._inchannels = inchannels
        self._outchannels = outchannels

    def process(self, stream):
        """Process a stream of data.

        Parameters
        ----------
        stream : obspy.core.Stream
            input data

        Returns
        -------
        obspy.core.Stream
            resulting data
        """
        return stream.copy()

    def get_input_channels(self):
        """Get input channels

        Returns
        -------
        array_like
            list of channels the algorithm needs to operate.
        """
        return self._inchannels

    def get_required_channels(self):
        """Get only required channels

        Returns
        -------
        array_like
            list of channels essential to the algorithm
        """
        return self._inchannels

    def get_output_channels(self):
        """Get output channels

        Returns
        -------
        array_like
            list of channels the algorithm will be returning.
        """
        return self._outchannels

    def get_input_interval(self, start, end, observatory=None, channels=None):
        """Get Input Interval

        start : UTCDateTime
            start time of requested output.
        end : UTCDateTime
            end time of requested output.
        observatory : string
            observatory code.
        channels : string
            input channels.

        Returns
        -------
        input_start : UTCDateTime
            start of input required to generate requested output
        input_end : UTCDateTime
            end of input required to generate requested output.
        """
        return (start, end)

    def can_produce_data(self, starttime, endtime, stream):
        """Can Product data

        Parameters
        ----------
        starttime: UTCDateTime
            start time of requested output
        end : UTCDateTime
            end time of requested output
        stream: obspy.core.Stream
            The input stream we want to make certain has data for the algorithm
        """
        input_gaps = TimeseriesUtility.get_merged_gaps(
                TimeseriesUtility.get_stream_gaps(stream))
        for input_gap in input_gaps:
            # Check for gaps that include the entire range
            if (starttime >= input_gap[0] and
                    starttime <= input_gap[1] and
                    endtime < input_gap[2]):
                return False
        return True

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.

        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """
        pass

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.

        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        self._inchannels = arguments.inchannels
        self._outchannels = arguments.outchannels or arguments.inchannels

    @classmethod
    def create_trace(cls, channel, stats, data):
        """Utility to create a new trace object.

        Parameters
        ----------
        channel : str
            channel name.
        stats : obspy.core.Stats
            channel metadata to clone.
        data : numpy.array
            channel data.

        Returns
        -------
        obspy.core.Trace
            trace containing data and metadata.
        """
        stats = obspy.core.Stats(stats)
        stats.channel = channel
        return obspy.core.Trace(data, stats)
