"""Stream wrapper for TimeseriesFactory."""
from __future__ import absolute_import

from .TimeseriesFactory import TimeseriesFactory


class StreamTimeseriesFactory(TimeseriesFactory):
    """Timeseries Factory for streams.
        normally stdio.

    Parameters
    ----------
    factory: geomagio.TimeseriesFactory
        wrapped factory.
    stream: file object
        io stream, normally either a file, or stdio

    See Also
    --------
    Timeseriesfactory
    """

    def __init__(self, factory, stream):
        self.factory = factory
        self.stream = stream
        self.stream_data = None

    def get_timeseries(
        self,
        starttime,
        endtime,
        observatory=None,
        channels=None,
        type=None,
        interval=None,
    ):
        """Get timeseries using stream as input."""
        if self.stream_data is None:
            # only read stream once
            self.stream_data = self.stream.read()
        return self.factory.parse_string(
            data=self.stream_data,
            starttime=starttime,
            endtime=endtime,
            observatory=observatory,
        )

    def put_timeseries(
        self,
        timeseries,
        starttime=None,
        endtime=None,
        channels=None,
        type=None,
        interval=None,
    ):
        """Put timeseries using stream as output."""
        self.factory.write_file(self.stream, timeseries, channels)
