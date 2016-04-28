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

    # Flag "output" used for vbf file versus bin-change log.
    def __init__(self, stream, observatory=None, channels=None,
            type=None, interval=None, output='vbf'):
        VBFFactory.__init__(self, None, observatory, channels,
            type, interval, output)
        self._stream = stream

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Implements get_timeseries

        Notes: Calls VBFFactory.parse_string in place of
            VBFFactory.get_timeseries.
        """
        return VBFFactory.parse_string(self, self._stream.read())

    def put_timeseries(self, timeseries, starttime=None, endtime=None,
            channels=None, type=None, interval=None):
        """Implements put_timeseries

        Notes: Calls VBFFactory.write_file in place of
            VBFFactory.get_timeseries. This can result in a
            non-standard VBF file, specifically one of longer than
            expected length.
        """
        VBFFactory.write_file(self, self._stream, timeseries, channels)
