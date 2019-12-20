"""Factory that loads IAGA2002 Files."""
from __future__ import absolute_import

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from .IAGA2002Parser import IAGA2002Parser
from .IAGA2002Writer import IAGA2002Writer


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

    def parse_string(self, data, observatory=None, interval='minute',
            **kwargs):
        """Parse the contents of a string in the format of an IAGA2002 file.

        Parameters
        ----------
        iaga2002String : str
            string containing IAGA2002 content.
        observatory : str
            observatory in case headers are unavailable.
            parses observatory from headers when available.
        Returns
        -------
        obspy.core.Stream
            parsed data.
        """
        parser = IAGA2002Parser(observatory=observatory)
        parser.parse(data)
        stream = obspy.core.Stream()
        if len(parser.times) == 0:
            # no data parsed
            return stream
        metadata = parser.metadata
        starttime = obspy.core.UTCDateTime(parser.times[0])
        endtime = obspy.core.UTCDateTime(parser.times[-1])
        data = parser.data
        length = len(data[list(data)[0]])
        if starttime != endtime:
            rate = (length - 1) / (endtime - starttime)
        else:
            # guess based on args
            if interval == 'minute':
                rate = 1 / 60
            elif interval == 'second':
                rate = 1
            else:
                raise Exception('one sample, and unable to guess rate')
        for channel in list(data.keys()):
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
