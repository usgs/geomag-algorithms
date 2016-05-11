"""Factory that loads IAGA2002 Files."""

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from ..TimeseriesFactoryException import TimeseriesFactoryException
from IAGA2002Parser import IAGA2002Parser
from IAGA2002Writer import IAGA2002Writer


# pattern for iaga 2002 file names
IAGA_FILE_PATTERN = '%(obs)s%(ymd)s%(t)s%(i)s.%(i)s'


class IAGA2002Factory(TimeseriesFactory):
    """TimeseriesFactory for IAGA 2002 formatted files.

    Parameters
    ----------
    urlTemplate : str
        A string that contains any of the following replacement patterns:
        - '%(i)s' : interval abbreviation
        - '%(interval)s' interval name
        - '%(obs)s' lowercase observatory code
        - '%(OBS)s' uppercase observatory code
        - '%(t)s' type abbreviation
        - '%(type)s' type name
        - '%(ymd)s' time formatted as YYYYMMDD

    See Also
    --------
    IAGA2002Parser
    """

    def __init__(self, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Get timeseries data

        Parameters
        ----------
        observatory : str
            observatory code.
        starttime : obspy.core.UTCDateTime
            time of first sample.
        endtime : obspy.core.UTCDateTime
            time of last sample.
        type : {'variation', 'quasi-definitive'}
            data type.
        interval : {'minute', 'second'}
            data interval.

        Returns
        -------
        obspy.core.Stream
            timeseries object with requested data.

        Raises
        ------
        TimeseriesFactoryException
            if invalid values are requested, or errors occur while
            retrieving timeseries.
        """
        return self._get_timeseries(
                starttime=starttime,
                endtime=endtime,
                observatory=observatory,
                channels=channels,
                type=type,
                interval=interval)

    def parse_string(self, iaga2002String):
        """Parse the contents of a string in the format of an IAGA2002 file.

        Parameters
        ----------
        iaga2002String : str
            string containing IAGA2002 content.

        Returns
        -------
        obspy.core.Stream
            parsed data.
        """
        parser = IAGA2002Parser()
        parser.parse(iaga2002String)
        metadata = parser.metadata
        starttime = obspy.core.UTCDateTime(parser.times[0])
        endtime = obspy.core.UTCDateTime(parser.times[-1])
        data = parser.data
        length = len(data[data.keys()[0]])
        rate = (length - 1) / (endtime - starttime)
        stream = obspy.core.Stream()
        for channel in data.keys():
            stats = obspy.core.Stats(metadata)
            stats.starttime = starttime
            stats.sampling_rate = rate
            stats.npts = length
            stats.channel = channel
            if channel == 'D':
                data[channel] = ChannelConverter.get_radians_from_minutes(
                    data[channel])
            stream += obspy.core.Trace(data[channel], stats)
        return stream

    def _get_days(self, starttime, endtime):
        """Get days between (inclusive) starttime and endtime.

        Parameters
        ----------
        starttime : obspy.core.UTCDateTime
            the start time
        endtime : obspy.core.UTCDateTime
            the end time

        Returns
        -------
        array_like
            list of times, one per day, for all days between and including
            ``starttime`` and ``endtime``.

        Raises
        ------
        TimeseriesFactoryException
            if starttime is after endtime
        """
        if starttime > endtime:
            raise TimeseriesFactoryException(
                    'starttime must be before endtime')
        days = []
        day = starttime
        lastday = (endtime.year, endtime.month, endtime.day)
        while True:
            days.append(day)
            if lastday == (day.year, day.month, day.day):
                break
            # move to next day
            day = obspy.core.UTCDateTime(day.timestamp + 86400)
        return days

    def write_file(self, fh, timeseries, channels):
        """writes timeseries data to the given file object.

        Parameters
        ----------
        fh: file object
        timeseries : obspy.core.Stream
            stream containing traces to store.
        channels : array_like
            list of channels to store
        """
        IAGA2002Writer().write(fh, timeseries, channels)

    def put_timeseries(self, timeseries, starttime=None, endtime=None,
            channels=None, type=None, interval=None):
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
        """
        if not self.urlTemplate.startswith('file://'):
            raise TimeseriesFactoryException('Only file urls are supported')
        channels = channels or self.channels
        type = type or self.type
        interval = interval or self.interval
        stats = timeseries[0].stats
        observatory = stats.station
        starttime = starttime or stats.starttime
        endtime = endtime or stats.endtime
        days = self._get_days(starttime, endtime)
        for day in days:
            day_filename = self._get_file_from_url(
                    self._get_url(observatory, day, type, interval))
            day_timeseries = self._get_slice(timeseries, day, interval)
            with open(day_filename, 'wb') as fh:
                self.write_file(fh, day_timeseries, channels)

    def _get_slice(self, timeseries, day, interval):
        """Get the first and last time for a day

        Parameters
        ----------
        timeseries : obspy.core.Stream
            timeseries to slice
        day : UTCDateTime
            time in day to slice

        Returns
        -------
        obspy.core.Stream
            sliced stream
        """
        day = day.datetime
        start = obspy.core.UTCDateTime(day.year, day.month, day.day, 0, 0, 0)
        if interval == 'minute':
            end = start + 86340.0
        else:
            end = start + 86399.999999
        return timeseries.slice(start, end)
