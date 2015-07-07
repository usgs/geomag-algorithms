"""Factory to load IAGA2002 files from an input StreamIAGA2002Factory."""

from IAGA2002Factory import IAGA2002Factory


class StreamIAGA2002Factory(IAGA2002Factory):
    """Timeseries Factory for IAGA2002 formatted files loaded via a stream.
        normally either a single file, or stdio.

    Parameters
    ----------
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    IAGA2002Factory
    Timeseriesfactory
    """
    def __init__(self, stream, observatory=None, channels=None,
            type=None, interval=None):
        IAGA2002Factory.__init__(self, None, observatory, channels,
            type, interval)
        self._stream = stream

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Implements get_timeseries

        Notes: Calls IAGA2002Factory.parse_string in place of
            IAGA2002Factory.get_timeseries.
        """

        self._stream.seek(0)
        return IAGA2002Factory.parse_string(self, self._stream.read())

    def put_timeseries(self, timeseries, starttime=None, endtime=None,
            channels=None, type=None, interval=None):
        """Implements put_timeseries

        Notes: Calls IAGA2002Factory.write_file in place of
            IAGA2002Factory.get_timeseries. This can result in a
            non-standard IAGA2002 file, specifically one of longer then
            expected length.
        """
        IAGA2002Factory.write_file(self, self._stream, timeseries, channels)
