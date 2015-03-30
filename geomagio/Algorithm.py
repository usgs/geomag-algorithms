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

    def __init__(self, channels=None):
        self._channels = channels
        pass

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
        return self._channels

    def get_output_channels(self):
        """Get output channels

        Returns
        -------
        array_like
            list of channels the algorithm will be returning.
        """
        return self._channels
