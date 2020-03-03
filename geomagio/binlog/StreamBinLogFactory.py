"""Factory to load BinLog files from an input StreamBinLogFactory."""
from __future__ import absolute_import

from .BinLogFactory import BinLogFactory


class StreamBinLogFactory(BinLogFactory):
    """Timeseries Factory for BinLog files loaded via a stream.
        normally either a single file, or stdio.

    Parameters
    ----------
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    BinLogFactory
    Timeseriesfactory
    """

    def __init__(self, stream, **kwargs):
        BinLogFactory.__init__(self, **kwargs)
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

        Notes: Calls BinLogFactory.write_file in place of
            BinLogFactory.put_timeseries. This can result in a
            non-standard BinLog file, specifically one of longer than
            expected length.
        """
        BinLogFactory.write_file(self, self._stream, timeseries, channels)
