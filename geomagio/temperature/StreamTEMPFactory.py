"""Factory to load temp/volt files from an input StreamTEMPFactory."""
from __future__ import absolute_import

from .TEMPFactory import TEMPFactory


class StreamTEMPFactory(TEMPFactory):
    """Timeseries Factory for temp/volt formatted files loaded via a stream.
        normally either a single file, or stdio.

    Parameters
    ----------
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    TEMPFactory
    Timeseriesfactory
    """

    def __init__(self, stream, **kwargs):
        TEMPFactory.__init__(self, **kwargs)
        self._stream = stream

    def put_timeseries(
        self,
        timeseries,
        starttime=None,
        endtime=None,
        channels=None,
        type=None,
        interval=None,
    ):
        """Implements put_timeseries

        Notes: Calls TEMPFactory.write_file in place of
            TEMPFactory.put_timeseries. This can result in a
            non-standard TEMP file, specifically one of longer than
            expected length.
        """
        TEMPFactory.write_file(self, self._stream, timeseries, channels)
