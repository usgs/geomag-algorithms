"""Factory that loads IAGA2002 Files."""

import urllib2
import obspy.core
from geomag.io import Timeseries, TimeseriesFactory, TimeseriesFactoryException
from IAGA2002Parser import IAGA2002Parser


# pattern for iaga 2002 file names
IAGA_FILE_PATTERN = '%(obs)s%(ymd)s%(t)s%(i)s.%(i)s'


def read_url(url):
    """Open and read url contents.

    Parameters
    ----------
    url : str
        A urllib2 compatible url, such as http:// or file://.

    Returns
    -------
    str
        contents returned by url.

    Raises
    ------
    urllib2.URLError
        if any occurs
    """
    response = urllib2.urlopen(url)
    content = None
    try:
        content = response.read()
    except urllib2.URLError, e:
        print e.reason
        raise
    finally:
        response.close()
    return content


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

    def __init__(self, urlTemplate):
        self.urlTemplate = urlTemplate

    def get_timeseries(self, observatory, starttime, endtime,
            type='variation', interval='minute'):
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
        days = self._get_days(starttime, endtime)
        timeseries = obspy.core.Stream()
        for day in days:
            url = self._get_url(observatory, day, type, interval)
            timeseries += self._parse_url(url, type, interval)
        timeseries.merge()
        return timeseries

    def _parse_url(self, url, type, interval):
        """Parse the contents of a url to an IAGA2002 file.

        Parameters
        ----------
        url : str
            url containing IAGA2002 content.

        Returns
        -------
        obspy.core.Stream
            parsed data.
        """
        parser = IAGA2002Parser()
        parser.parse(read_url(url))
        headers = parser.headers;
        station = headers['IAGA CODE']
        comments = parser.comments;
        starttime = parser.times[0];
        endtime = parser.times[-1];
        data = parser.data
        length = len(data[data.keys()[0]])
        rate = (length - 1) / (endtime - starttime)
        stream = obspy.core.Stream()
        for channel in data.keys():
            stats = obspy.core.Stats(headers)
            stats.comments = comments
            stats.starttime = starttime
            stats.sampling_rate = rate
            stats.npts = length
            stats.network = 'IAGA'
            stats.station = station
            stats.channel = channel
            stats.type = type
            stats.interval = interval
            stream += obspy.core.Trace(data[channel], stats)
        return stream

    def _get_url(self, observatory, date, type='variation', interval='minute'):
        """Get the url for a specified IAGA2002 file.

        Replaces patterns (described in class docstring) with values based on
        parameter values.

        Parameters
        ----------
        observatory : str
            observatory code.
        date : obspy.core.UTCDateTime
            day to fetch (only year, month, day are used)
        type : {'variation', 'quasi-definitive'}
            data type.
        interval : {'minute', 'second'}
            data interval.

        Raises
        ------
        TimeseriesFactoryException
            if type or interval are not supported.
        """
        return self.urlTemplate % {
                'i': self._get_interval_abbreviation(interval),
                'interval': self._get_interval_name(interval),
                'obs': observatory.lower(),
                'OBS': observatory.upper(),
                't': self._get_type_abbreviation(type),
                'type': self._get_type_name(type),
                'ymd': date.strftime("%Y%m%d")}

    def _get_interval_abbreviation(self, interval):
        """Get abbreviation for a data interval.

        Used by ``_get_url`` to replace ``%(i)s`` in urlTemplate.

        Parameters
        ----------
        interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}

        Returns
        -------
        abbreviation for ``interval``.

        Raises
        ------
        TimeseriesFactoryException
            if ``interval`` is not supported.
        """
        interval_abbr = None
        if interval == 'daily':
            interval_abbr = 'day'
        elif interval == 'hourly':
            interval_abbr = 'hor'
        elif interval == 'minute':
            interval_abbr = 'min'
        elif interval == 'monthly':
            interval_abbr = 'mon'
        elif interval == 'second':
            interval_abbr = 'sec'
        else:
            raise TimeseriesFactoryException(
                    'Unexpected interval "%s"' % interval)
        return interval_abbr

    def _get_interval_name(self, interval):
        """Get name for a data interval.

        Used by ``_get_url`` to replace ``%(interval)s`` in urlTemplate.

        Parameters
        ----------
        interval : {'minute', 'second'}

        Returns
        -------
        name for ``interval``.

        Raises
        ------
        TimeseriesFactoryException
            if ``interval`` is not supported.
        """
        interval_name = None
        if interval == 'minute':
            interval_name = 'OneMinute'
        elif interval == 'second':
            interval_name = 'OneSecond'
        else:
            raise TimeseriesFactoryException(
                    'Unsupported interval "%s"' % interval)
        return interval_name
    
    def _get_type_abbreviation(self, type):
        """Get abbreviation for a data type.

        Used by ``_get_url`` to replace ``%(t)s`` in urlTemplate.

        Parameters
        ----------
        type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}

        Returns
        -------
        name for ``type``.

        Raises
        ------
        TimeseriesFactoryException
            if ``type`` is not supported.
        """
        type_abbr = None
        if type == 'definitive':
            type_abbr = 'd'
        elif type == 'provisional':
            type_abbr = 'p'
        elif type == 'quasi-definitive':
            type_abbr = 'q'
        elif type == 'variation':
            type_abbr = 'v'
        else:
            raise TimeseriesFactoryException(
                    'Unexpected type "%s"' % type)
        return type_abbr

    def _get_type_name(self, type):
        """Get name for a data type.

        Used by ``_get_url`` to replace ``%(type)s`` in urlTemplate.

        Parameters
        ----------
        type : {'variation', 'quasi-definitive'}

        Returns
        -------
        name for ``type``.

        Raises
        ------
        TimeseriesFactoryException
            if ``type`` is not supported.
        """
        type_name = None
        if type == 'variation':
            type_name = ''
        elif type == 'quasi-definitive':
            type_name = 'QuasiDefinitive'
        else:
            raise TimeseriesFactoryException(
                    'Unsupported type "%s"' % type)
        return type_name

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
