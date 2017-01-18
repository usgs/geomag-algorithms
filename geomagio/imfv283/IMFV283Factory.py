"""Factory that loads IAGA2002 Files."""
from __future__ import absolute_import

import numpy
from .. import ChannelConverter
from ..TimeseriesFactory import TimeseriesFactory
from .IMFV283Parser import IMFV283Parser
from ..ObservatoryMetadata import ObservatoryMetadata


class IMFV283Factory(TimeseriesFactory):
    """TimeseriesFactory for IMFV283 formatted files.

    See Also
    --------
    IMFV283Parser

    Notes
    -----
    The urlTemplate is probably overkill for IMFV283, but I've left it in place
    in case someone has a different methodology, that more closely models the
    url/file reading.
    """

    def __init__(self, observatoryMetadata=None, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)
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
        timeseries = TimeseriesFactory.get_timeseries(
                self,
                starttime=starttime,
                endtime=endtime,
                observatory=observatory,
                channels=channels,
                type=type,
                interval=interval)
        observatory = observatory or self.observatory
        if observatory is not None:
            timeseries = timeseries.select(station=observatory)
        for trace in timeseries:
            stats = trace.stats
            self.observatoryMetadata.set_metadata(stats, stats.station,
                    stats.channel, 'variation', 'minute')
        return timeseries

    def parse_string(self, data, **kwargs):
        """Parse the contents of a string in the format of an IMFV283 file.

        Parameters
        ----------
        data : str
            string containing IMFV283 content.

        Returns
        -------
        obspy.core.Stream
            parsed data.
        """
        parser = IMFV283Parser()
        parser.parse(data)

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
