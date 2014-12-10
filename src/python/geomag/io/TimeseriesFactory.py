"""Abstract Timeseries Factory Interface."""


class TimeseriesFactory(object):
    """Base class for timeseries factories."""

    def get_timeseries(self, observatory, starttime, endtime,
            channels=('H', 'D', 'Z', 'F'),
            type='variation', interval='minute'):
        """Get timeseries data.

        Support for specific channels, types, and intervals varies
        between factory and observatory.  Subclasses should raise
        TimeseriesFactoryException if the data is not available, or
        if an error occurs accessing data.

        Parameters
        ----------
        observatory : str
            observatory code, usually 3 characters.
        starttime : UTCDateTime
            time of first sample in timeseries.
        endtime : UTCDateTime
            time of last sample in timeseries.
        channels : array_like
            list of channels to load.
        type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
            data type.
        interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
            data interval.

        Returns
        -------
        obspy.core.Stream
            stream containing traces for requested timeseries.

        Raises
        ------
        TimeseriesFactoryException
            if any parameters are unsupported, or errors occur loading data.
        """
        raise NotImplementedError('"get_timeseries" not implemented')

    def put_timeseries(self, timeseries, channels):
        """Store timeseries data.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces to store.
        channels : list
            list of channels to store.

        Raises
        ------
        TimeseriesFactoryException
            if any errors occur.
        """
        raise NotImplementedError('"put_timeseries" not implemented')
