"""Factory that loads PCDCP Files."""
from __future__ import absolute_import

import obspy.core
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from .PCDCPParser import PCDCPParser
from .PCDCPWriter import PCDCPWriter


# pattern for pcdcp file names
PCDCP_FILE_PATTERN = "%(OBS)s%(year)s%(julian)s.%(i)s"
# note: seconds files end in .raw after 2008, .sec or .Sec on or before


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

    def __init__(
        self,
        temperatures=False,
        **kwargs,
    ):
        TimeseriesFactory.__init__(self, **kwargs)
        self.temperatures = temperatures

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
        if not parser.times:
            return obspy.core.Stream()

        # minutes files times are 4 characters long (1440)
        # seconds files times are 5 characters long (86400)
        sample_periods = {4: 60.0, 5: 1.0}
        sample_period = sample_periods[len(parser.times[0])]

        yr = parser.header["year"]
        yrday = parser.header["yearday"]

        startday = obspy.core.UTCDateTime(yr + yrday)
        starttime = startday + int(parser.times[0]) * sample_period
        endtime = startday + int(parser.times[-1]) * sample_period

        data = parser.data
        length = len(data[list(data)[0]])
        rate = (length - 1) / (endtime - starttime)
        stream = obspy.core.Stream()

        for channel in list(data.keys()):
            stats = obspy.core.Stats()
            stats.network = "NT"
            stats.station = parser.header["station"]
            stats.starttime = starttime
            stats.sampling_rate = rate
            stats.npts = length
            stats.channel = channel

            if channel == "D":
                data[channel] = ChannelConverter.get_radians_from_minutes(data[channel])

            stream += obspy.core.Trace(data[channel], stats)

        return stream

    def _get_interval_abbreviation(self, interval):
        """Get abbreviation for a data interval.

        Used by ``TimeseriesFactory._get_url`` to replace ``%(i)s`` in urlTemplate if interval is not seconds.
        Returns "raw" if interval is seconds.

        Parameters
        ----------
        interval : {'minute', 'second'}

        Returns
        -------
        abbreviation for ``interval``.
        """
        if interval == "second":
            return "raw"
        return super()._get_interval_abbreviation(interval)

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
        PCDCPWriter(temperatures=self.temperatures).write(fh, timeseries, channels)
