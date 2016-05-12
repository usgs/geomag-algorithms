"""Factory that loads IAGA2002 Files."""

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
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
        return self._put_timeseries(
                timeseries=timeseries,
                starttime=starttime,
                endtime=endtime,
                channels=channels,
                type=type,
                interval=interval)

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
