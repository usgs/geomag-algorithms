"""Algorithm Interface."""


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

    def get_output_channels(self):
        """Get output channels

        Returns
        -------
        array_like
            list of channels the algorithm will be returning.
        """
        return self._outchannels

    def get_input_interval(self, start, end):
        """Get Input Interval

        start : UTCDateTime
            start time of requested output
        end : UTCDateTime
            end time of requested output

        Returns
        -------
        tuple : (input_start, input_end)
            start and end of required input to generate requested output.
        """
        return (start, end)
