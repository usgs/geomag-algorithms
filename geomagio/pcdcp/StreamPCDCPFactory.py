"""Factory to load PCDCP files from an input StreamPCDCPFactory."""

from PCDCPFactory import PCDCPFactory


class StreamPCDCPFactory(PCDCPFactory):
    """Timeseries Factory for PCDCP formatted files loaded via a stream.
        normally either a single file, or stdio.

    Parameters
    ----------
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    PCDCPFactory
    Timeseriesfactory
    """
    def __init__(self, stream, observatory=None, channels=None,
            type=None, interval=None):
        PCDCPFactory.__init__(self, None, observatory, channels,
            type, interval)
        self._stream = stream

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Implements get_timeseries

        Notes: Calls PCDCPFactory.parse_string in place of
            PCDCPFactory.get_timeseries.
        """
        return PCDCPFactory.parse_string(self, self._stream.read())

    def put_timeseries(self, timeseries, starttime=None, endtime=None,
            channels=None, type=None, interval=None):
        """Implements put_timeseries

        Notes: Calls PCDCPFactory.write_file in place of
            PCDCPFactory.get_timeseries. This can result in a
            non-standard PCDCP file, specifically one of longer than
            expected length.
        """
        PCDCPFactory.write_file(self, self._stream, timeseries, channels)
