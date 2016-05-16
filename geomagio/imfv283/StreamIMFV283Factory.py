"""Factory to load IMFV283 files from an input StreamIMFV283Factory."""

from IMFV283Factory import IMFV283Factory


class StreamIMFV283Factory(IMFV283Factory):
    """Timeseries Factory for IMFV283 formatted files loaded via a stream.
        normally either a single file, or stdio.

    Parameters
    ----------
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    IMFV283Factory
    Timeseriesfactory
    """
    def __init__(self, stream, **kwargs):
        IMFV283Factory.__init__(self, **kwargs)
        self._stream = stream

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Implements get_timeseries

        Notes: Calls IMFV283Factory.parse_string in place of
            IMFV283Factory.get_timeseries.
        """
        return IMFV283Factory.parse_string(self, self._stream.read())
