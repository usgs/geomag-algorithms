"""Abstract Timeseries Factory Interface."""
from __future__ import absolute_import

from obspy.core import Stream
from .TimeseriesFactory import TimeseriesFactory


class PlotTimeseriesFactory(TimeseriesFactory):
    """TimeseriesFactory that generates a plot."""

    def __init__(self, *args, **kwargs):
        TimeseriesFactory.__init__(self, *args, **kwargs)

    def get_timeseries(
        self,
        starttime,
        endtime,
        observatory=None,
        channels=None,
        type=None,
        interval=None,
    ):
        """This factory does not support get_timeseries."""
        raise NotImplementedError('"get_timeseries" not implemented')

    def put_timeseries(
        self,
        timeseries,
        starttime=None,
        endtime=None,
        channels=None,
        type=None,
        interval=None,
    ):
        """Store timeseries data.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces to store.
        starttime : UTCDateTime
            time of first sample in timeseries to store.
            uses first sample if unspecified.
        endtime : UTCDateTime
            time of last sample in timeseries to store.
            uses last sample if unspecified.
        channels : array_like
            list of channels to store, optional.
            uses default if unspecified.
        type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
            data type, optional.
            uses default if unspecified.
        interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
            data interval, optional.
            uses default if unspecified.
        Raises
        ------
        TimeseriesFactoryException
            if any errors occur.
        """
        if starttime is not None or endtime is not None:
            timeseries = timeseries.copy()
            timeseries.trim(starttime=starttime, endtime=endtime)
        if channels is not None:
            filtered = Stream()
            for channel in channels:
                filtered += timeseries.select(channel=channel)
            timeseries = filtered
        timeseries.plot()
