"""Factory that loads VBF Files."""
from __future__ import absolute_import

from ..TimeseriesFactory import TimeseriesFactory
from .VBFWriter import VBFWriter


# pattern for vbf file names
VBF_FILE_PATTERN = "%(obs)s%(y)s%(j)s.%(i)s"


class VBFFactory(TimeseriesFactory):
    """TimeseriesFactory for VBF formatted files.

    Parameters
    ----------
    output : vbf style output.

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
        VBFWriter().write(fh, timeseries, channels)
