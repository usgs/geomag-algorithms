"""Factory that creates BinLog Files."""

from ..TimeseriesFactory import TimeseriesFactory
from BinLogWriter import BinLogWriter


class BinLogFactory(TimeseriesFactory):
    """TimeseriesFactory for BinLog formatted files.

    Parameters
    ----------
    output : bin-change report.

    All other named parameters passed to TimeseriesFactory.

    See Also
    --------
    TimeseriesFactory
    """

    def __init__(self, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)

    def write_file(self, fh, timeseries, channels):
        """Write timeseries data to the given file object.

        Parameters
        ----------
        fh : writable
            file handle where data is written.
        timeseries : obspy.core.Stream
            stream containing traces to store.
        channels : list
            list of channels to store.
        """
        BinLogWriter().write(fh, timeseries, channels)
