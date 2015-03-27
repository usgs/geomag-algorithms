

class Algorithm(object):
    """An algorithm processes a stream of timeseries to produce new timeseries.
    """

    def __init__(self, channels=None):
        self._channels = channels
        pass

    def process(self, stream):
        """Process a chunk of data.

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
        return self._channels

    def get_output_channels(self):
        return self._channels
