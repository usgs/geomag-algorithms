"""Factory that loads IAGA2002 Files."""

import obspy.core
import numpy
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from ..TimeseriesFactoryException import TimeseriesFactoryException
from ..Util import read_url
from IMFV283Parser import IMFV283Parser
from ..ObservatoryMetadata import ObservatoryMetadata


class IMFV283Factory(TimeseriesFactory):
    """TimeseriesFactory for IMFV283 formatted files.

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
            interval=None, observatoryMetadata=None):
        TimeseriesFactory.__init__(self, observatory, channels, type,
                interval, urlTemplate)
        self.observatoryMetadata = observatoryMetadata or ObservatoryMetadata()

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
        url_id = self._get_url(observatory, obspy.core.UTCDateTime(),
                type, interval)

        imfV283File = read_url(url_id)
        timeseries += self.parse_string(imfV283File)
        # merge channel traces for multiple days
        timeseries.merge()
        # trim to requested start/end time
        timeseries.trim(starttime, endtime)
        self._post_process(timeseries)
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

    def _post_process(self, timeseries):
        for trace in timeseries:
            stats = trace.stats
            self.observatoryMetadata.set_metadata(stats, stats.station,
                    stats.channel, 'variation', 'minute')
