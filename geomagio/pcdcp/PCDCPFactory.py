"""Factory that loads PCDCP Files."""
from __future__ import absolute_import

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from .PCDCPParser import PCDCPParser
from .PCDCPWriter import PCDCPWriter


# pattern for pcdcp file names
PCDCP_FILE_PATTERN = '%(obs)s%(y)s%(j)s.%(i)s'
# note: seconds files end in .raw, not .sec


class PCDCPFactory(TimeseriesFactory):
    """TimeseriesFactory for PCDCP formatted files.

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
    PCDCPParser
    """

    def __init__(self, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)

    def parse_string(self, data, **kwargs):
        """Parse the contents of a string in the format of a pcdcp file.

        Parameters
        ----------
        data : str
            String containing PCDCP content.

        Returns
        -------
        obspy.core.Stream
            Parsed data.
        """
        parser = PCDCPParser()
        parser.parse(data)

        yr = int(parser.header['year'])
        yrday = int(parser.header['yearday'])

        begin = int(parser.times[0])
        startHour = int(begin / 60.0)
        startMinute = int(begin % 60.0)
        ending = int(parser.times[-1])
        endHour = int(ending / 60.0)
        endMinute = int(ending % 60.0)

        starttime = obspy.core.UTCDateTime(year=yr, julday=yrday,
                        hour=startHour, minute=startMinute)
        endtime = obspy.core.UTCDateTime(year=yr, julday=yrday, hour=endHour,
                        minute=endMinute)

        data = parser.data
        length = len(data[list(data)[0]])
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
        PCDCPWriter().write(fh, timeseries, channels)
