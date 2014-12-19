

class Algorithm(object):
    """An algorithm processes a stream of timeseries to produce new timeseries.
    """

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
