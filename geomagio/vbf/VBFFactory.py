"""Factory that loads VBF Files."""

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from ..TimeseriesFactoryException import TimeseriesFactoryException
from ..Util import read_url
from VBFParser import VBFParser
from VBFWriter import VBFWriter


# pattern for vbf file names
VBF_FILE_PATTERN = '%(obs)s%(y)s%(j)s.%(i)s'


class VBFFactory(TimeseriesFactory):
    """TimeseriesFactory for VBF formatted files.

    Parameters
    ----------
    urlTemplate : str
        A string that contains any of the following replacement patterns:
        - '%(i)s' : interval abbreviation
        - '%(interval)s' interval name
        - '%(julian)s' julian day formatted as JJJ
        - '%(obs)s' lowercase observatory code
        - '%(OBS)s' uppercase observatory code
        - '%(t)s' type abbreviation
        - '%(type)s' type name
        - '%(year)s' year formatted as YYYY
        - '%(ymd)s' time formatted as YYYYMMDD

    See Also
    --------
    VBFParser
    """

    # DCS -- 20160401 -- output flag added to parm list for vbf vs binlog
    def __init__(self, urlTemplate, observatory=None, channels=None, type=None,
            interval=None, output='vbf'):
        TimeseriesFactory.__init__(self, observatory, channels, type,
                interval, urlTemplate)
        self.output = output

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Get timeseries data

        Parameters
        ----------
        observatory : str
            3-letter observatory code.
        starttime : obspy.core.UTCDateTime
            Time of first sample.
        endtime : obspy.core.UTCDateTime
            Time of last sample.
        type : {'variation', 'quasi-definitive'}
            Data type.
        interval : {'minute', 'second'}
            Data interval.

        Returns
        -------
        obspy.core.Stream
            timeseries object with requested data.

        Raises
        ------
        TimeseriesFactoryException
            If invalid values are requested, or errors occur while
            retrieving timeseries.
        """
        observatory = observatory or self.observatory
        channels = channels or self.channels
        type = type or self.type
        interval = interval or self.interval
        days = self._get_days(starttime, endtime)
        timeseries = obspy.core.Stream()
        for day in days:
            url_id = self._get_url(observatory, day, type, interval)
            vbfFile = read_url(url_id)
            timeseries += self.parse_string(vbfFile)

        # merge channel traces for multiple days
        timeseries.merge()

        # trim to requested start/end time
        timeseries.trim(starttime, endtime)

        return timeseries

    def parse_string(self, vbfString):
        """Parse the contents of a string in the format of a vbf file.

        Parameters
        ----------
        vbfString : str
            String containing VBF content.

        Returns
        -------
        obspy.core.Stream
            Parsed data.
        """
        parser = VBFParser()
        parser.parse(vbfString)

        year = parser.header['year']
        yearday = parser.header['yearday']

        begin = int(parser.times[0])
        startHour = str(int(begin / 60.0))
        startMinute = str(int(begin % 60.0))
        ending = int(parser.times[-1])
        endHour = str(int(ending / 60.0))
        endMinute = str(int(ending % 60.0))

        start = year + yearday + "T" + startHour + ":" + \
                startMinute + ":" + "00.0"
        end = year + yearday + "T" + endHour + ":" + endMinute + ":" + "00.0"

        starttime = obspy.core.UTCDateTime(start)
        endtime = obspy.core.UTCDateTime(end)

        data = parser.data
        length = len(data[data.keys()[0]])
        rate = (length - 1) / (endtime - starttime)
        stream = obspy.core.Stream()

        for channel in data.keys():
            stats = obspy.core.Stats()
            stats.network = 'NT'
            stats.station = parser.header['station']
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
                'starttime must be before endtime.')

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

        # DCS 20160401 -- if making a bin change log, call the _change_
        # version of 'write'. Otherwise, call the usual 'write'
        if self.output == 'binlog':
            VBFWriter().write_change_log(fh, timeseries, channels)
        else:
            VBFWriter().write(fh, timeseries, channels)

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
        print self.urlTemplate
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
