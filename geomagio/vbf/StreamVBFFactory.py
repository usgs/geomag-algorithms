"""Factory to load VBF files from an input StreamVBFFactory."""

from VBFFactory import VBFFactory


class StreamVBFFactory(VBFFactory):
    """Timeseries Factory for VBF formatted files loaded via a stream.
        normally either a single file, or stdio.

    Parameters
    ----------
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    VBFFactory
    Timeseriesfactory
    """

    def __init__(self, stream, **kwargs):
        VBFFactory.__init__(self, **kwargs)
        self._stream = stream

    def put_timeseries(self, timeseries, starttime=None, endtime=None,
            channels=None, type=None, interval=None):
        """Implements put_timeseries

        Notes: Calls VBFFactory.write_file in place of
            VBFFactory.put_timeseries. This can result in a
            non-standard VBF file, specifically one of longer than
            expected length.
        """
        VBFFactory.write_file(self, self._stream, timeseries, channels)
