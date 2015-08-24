"""Factory that loads IAGA2002 Files."""

import obspy.core
import os
import urllib2
import numpy
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from ..TimeseriesFactoryException import TimeseriesFactoryException
from IMFV283Parser import IMFV283Parser


# pattern for IMFV283 file names
IMFV283_FILE_PATTERN = 'dcpmsgs.txt'


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


class IMFV283Factory(TimeseriesFactory):
    """TimeseriesFactory for IMFV283 formatted files.

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
    IMFV283Parser

    Notes
    -----
    The urlTemplate is probably overkill for IMFV283, but I've left it in place
    in case some has a different methodology, that more closely models the
    url/file reading.
    """

    def __init__(self, urlTemplate, observatory=None, channels=None, type=None,
            interval=None):
        TimeseriesFactory.__init__(self, observatory, channels, type, interval)
        self.urlTemplate = urlTemplate

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type='variation', interval='minute'):
        """Get timeseries data

        Parameters
        ----------
        observatory : str
            observatory code.
        starttime : obspy.core.UTCDateTime
            time of first sample.
        endtime : obspy.core.UTCDateTime
            time of last sample.
        type : {'variation'}
            data type.
        interval : {'minute'}
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
        observatory = observatory or self.observatory
        channels = channels or self.channels
        type = type or self.type
        interval = interval or self.interval
        timeseries = obspy.core.Stream()

        url = self._get_url(observatory, obspy.core.UTCDateTime(),
                type, interval)
        imfV283File = read_url(url)
        timeseries += self.parse_string(imfV283File)
        # merge channel traces for multiple days
        timeseries.merge()
        # trim to requested start/end time
        timeseries.trim(starttime, endtime)
        if observatory is not None:
            timeseries = timeseries.select(station=observatory)
        return timeseries.select(station=observatory)

    def parse_string(self, imfV283String):
        """Parse the contents of a string in the format of an IMFV283 file.

        Parameters
        ----------
        IMFV283String : str
            string containing IMFV283 content.

        Returns
        -------
        obspy.core.Stream
            parsed data.
        """
        parser = IMFV283Parser()
        parser.parse(imfV283String)

        stream = parser.stream
        stream.merge()

        for trace in stream:
            if isinstance(trace.data, numpy.ma.MaskedArray):
                trace.data.set_fill_value(numpy.nan)
                trace.data = trace.data.filled()
        if stream.select(channel='D').count() > 0:
            for trace in stream.select(channel='D'):
                trace.data = ChannelConverter.get_radians_from_minutes(
                    trace.data)

        return stream

    def _get_url(self, observatory, date, type='variation', interval='minute'):
        """Get the url for a specified IMFV283 file.

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
        print interval
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
        raise TimeseriesFactoryException('IAF write_file not implemented.')

    def _get_file_from_url(self, url):
        """Get a file for writing.

        Ensures parent directory exists.

        Parameters
        ----------
        url : str
            Url path to IMFV283

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
