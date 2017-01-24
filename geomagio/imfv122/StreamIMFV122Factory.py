"""Factory to load IMFV122 files from an input stream."""
from __future__ import absolute_import

from .IMFV122Factory import IMFV122Factory


class StreamIMFV122Factory(IMFV122Factory):
    """Timeseries Factory for IMFV122 formatted files loaded via a stream.
        normally either a single file, or stdio.

    Parameters
    ----------
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    IMFV122Factory
    Timeseriesfactory
    """
    def __init__(self, stream, **kwargs):
        IMFV122Factory.__init__(self, **kwargs)
        self._stream = stream

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Implements get_timeseries

        Notes: Calls IMFV122Factory.parse_string in place of
            IMFV122Factory.get_timeseries.
        """
        return IMFV122Factory.parse_string(self,
                data=self._stream.read(),
                observatory=observatory)
