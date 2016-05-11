"""Abstract Timeseries Factory Interface."""
import obspy.core
import os
import sys
from TimeseriesFactoryException import TimeseriesFactoryException
import Util


class TimeseriesFactory(object):
    """Base class for timeseries factories.

    Attributes
    ----------
    observatory : str
        default observatory code, usually 3 characters.
    channels : array_like
        default list of channels to load, optional.
        default ('H', 'D', 'Z', 'F')
    type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
        default data type, optional.
        default 'variation'.
    interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
        data interval, optional.
        default 'minute'.
    urlTemplate : str
        A string that contains any of the following replacement patterns:
        - '%(i)s' : interval abbreviation
        - '%(interval)s' interval name
        - '%(julian)s' julian date
        - '%(obs)s' lowercase observatory code
        - '%(OBS)s' uppercase observatory code
        - '%(t)s' type abbreviation
        - '%(type)s' type name
        - '%(year)s' year formatted as YYYY
        - '%(ymd)s' time formatted as YYYYMMDD
    """
    def __init__(self, observatory=None, channels=('H', 'D', 'Z', 'F'),
            type='variation', interval='minute',
            urlTemplate='', urlInterval=-1):
        self.observatory = observatory
        self.channels = channels
        self.type = type
        self.interval = interval
        self.urlTemplate = urlTemplate
        self.urlInterval = urlInterval

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Get timeseries data.

        Support for specific channels, types, and intervals varies
        between factory and observatory.  Subclasses should raise
        TimeseriesFactoryException if the data is not available, or
        if an error occurs accessing data.

        Parameters
        ----------
        starttime : UTCDateTime
            time of first sample in timeseries.
        endtime : UTCDateTime
            time of last sample in timeseries.
        observatory : str
            observatory code, usually 3 characters, optional.
            uses default if unspecified.
        channels : array_like
            list of channels to load, optional.
            uses default if unspecified.
        type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
            data type, optional.
            uses default if unspecified.
        interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
            data interval, optional.
            uses default if unspecified.

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
        raise NotImplementedError('"parse_string" not implemented')

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
        Raises
        ------
        TimeseriesFactoryException
            if any errors occur.
        """
        raise NotImplementedError('"put_timeseries" not implemented')

    def _get_file_from_url(self, url):
        """Get a file for writing.

        Ensures parent directory exists.

        Parameters
        ----------
        url : str
            path to file

        Returns
        -------
        str
            path to file without file:// prefix

        Raises
        ------
        TimeseriesFactoryException
            if url does not start with file://
        """
        if not url.startswith('file://'):
            raise TimeseriesFactoryException(
                    'Only file urls are supported for writing')
        filename = url.replace('file://', '')
        parent = os.path.dirname(filename)
        if not os.path.exists(parent):
            os.makedirs(parent)
        return filename

    def _get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """A basic implementation of get_timeseries using parse_string.

        Parameters
        ----------
        starttime : UTCDateTime
            time of first sample in timeseries.
        endtime : UTCDateTime
            time of last sample in timeseries.
        observatory : str
            observatory code, usually 3 characters, optional.
            uses default if unspecified.
        channels : array_like
            list of channels to load, optional.
            uses default if unspecified.
        type : {'definitive', 'provisional', 'quasi-definitive', 'variation'}
            data type, optional.
            uses default if unspecified.
        interval : {'daily', 'hourly', 'minute', 'monthly', 'second'}
            data interval, optional.
            uses default if unspecified.

        Returns
        -------
        obspy.core.Stream
            stream containing traces for requested timeseries.
        """
        observatory = observatory or self.observatory
        channels = channels or self.channels
        type = type or self.type
        interval = interval or self.interval

        timeseries = obspy.core.Stream()
        urlIntervals = Util.get_intervals(
                starttime=starttime,
                endtime=endtime,
                size=self.urlInterval)
        for urlInterval in urlIntervals:
            url = self._get_url(
                    observatory=observatory,
                    date=urlInterval['start'],
                    type=type,
                    interval=interval,
                    channels=channels)
            data = Util.read_url(url)
            try:
                timeseries += self.parse_string(data)
            except Exception as e:
                print >> sys.stderr, "Error parsing data: " + str(e)
                print >> sys.stderr, data
        timeseries.merge()
        timeseries.trim(starttime, endtime)
        return timeseries

    def _get_url(self, observatory, date, type='variation', interval='minute',
            channels=None):
        """Get the url for a specified file.

        Replaces patterns (described in class docstring) with values based on
        parameter values.

        Parameters
        ----------
        observatory : str
            observatory code.
        date : obspy.core.UTCDateTime
            day to fetch (only year, month, day are used)
        type : {'variation', 'quasi-definitive', 'definitive'}
            data type.
        interval : {'minute', 'second', 'hourly', 'daily'}
            data interval.
        channels : list
            list of data channels being requested

        Raises
        ------
        TimeseriesFactoryException
            if type or interval are not supported.
        """
        params = {
            'i': self._get_interval_abbreviation(interval),
            'interval': self._get_interval_name(interval),
            'obs': observatory.lower(),
            'OBS': observatory.upper(),
            't': self._get_type_abbreviation(type),
            'type': self._get_type_name(type),
            'date': date.datetime,
            # deprecated date properties
            # used by Kakioka, upper/lower not supported in string.format
            'minute': date.hour * 60 + date.minute,
            'month': date.strftime('%b').lower(),
            'MONTH': date.strftime('%b').upper(),
            # LEGACY
            # old date properties, string.format supports any strftime format
            # i.e. '{date:%j}'
            'julian': date.strftime('%j'),
            'year': date.strftime('%Y'),
            'ymd': date.strftime('%Y%m%d')
        }
        if '{' in self.urlTemplate:
            # use new style string formatting
            return self.urlTemplate.format(**params)
        # use old style string interpolation
        return self.urlTemplate % params

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
