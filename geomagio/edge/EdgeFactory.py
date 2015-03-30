"""Factory that loads data from earthworm and writes to Edge.

EdgeFactory uses obspy earthworm class to read data from any
earthworm standard Waveserver using the obspy getWaveform call.

Writing will be implemented with Edge specific capabilities,
to take advantage of it's newer realtime abilities.

Edge is the USGS earthquake hazard centers replacement for earthworm.
"""

import obspy.core
from obspy.core.utcdatetime import UTCDateTime
import numpy
from geomagio import TimeseriesFactory, TimeseriesFactoryException
from obspy import earthworm
from ObservatoryMetadata import ObservatoryMetadata


class EdgeFactory(TimeseriesFactory):
    """TimeseriesFactory for Edge related data.

    Parameters
    ----------
    host: str
        a string representing the IP number of the host to connect to.
    port: integer
        the port number the waveserver is listening on.
    observatoryMetadata: ObservatoryMetadata object
        an ObservatoryMetadata object used to replace the default
        ObservatoryMetadata.

    See Also
    --------
    TimeseriesFactory
    """

    def __init__(self, host=None, port=None, observatory=None,
            channels=None, type=None, interval=None,
            observatoryMetadata=None):
        TimeseriesFactory.__init__(self, observatory, channels, type, interval)
        self.client = earthworm.Client(host, port)

        self.observatoryMetadata = observatoryMetadata or ObservatoryMetadata()

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Get timeseries data

        Parameters
        ----------
        starttime : obspy.core.UTCDateTime
            time of first sample.
        endtime : obspy.core.UTCDateTime
            time of last sample.
        observatory : str
            observatory code.
        channels : array_like
            list of channels to load
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
        observatory = observatory or self.observatory
        channels = channels or self.channels
        type = type or self.type
        interval = interval or self.interval

        if starttime > endtime:
            raise TimeseriesFactoryException(
                'Starttime before endtime "%s" "%s"' % (starttime, endtime))

        timeseries = obspy.core.Stream()
        for channel in channels:
            data = self._get_timeseries(starttime, endtime, observatory,
                    channel, type, interval)
            timeseries += data

        self._post_process(timeseries, starttime, endtime, channels)

        return timeseries

    def put_timeseries(self, starttime, endtime, observatory=None,
                channels=None, type=None, interval=None):
        """Put timeseries data

        Parameters
        ----------
        observatory : str
            observatory code.
        starttime : obspy.core.UTCDateTime
            time of first sample.
        endtime : obspy.core.UTCDateTime
            time of last sample.
        channels : array_like
            list of channels to load
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
        raise NotImplementedError('"put_timeseries" not implemented')

    def _convert_trace_to_decimal(self, stream):
        """convert geomag edge traces stored as ints, to decimal by dividing
           by 1000.00
        Parameters
        ----------
        stream : obspy.core.stream
            a stream retrieved from a geomag edge representing one channel.
        """
        for trace in stream:
            trace.data = numpy.divide(trace.data, 1000.00)

    def _get_edge_network(self, observatory, channel, type, interval):
        """get edge network code.

        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        network
            always NT
        """
        return 'NT'

    def _get_edge_station(self, observatory, channel, type, interval):
        """get edge station.

        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        station
            the observatory is returned as the station
        """
        return observatory

    def _get_edge_channel(self, observatory, channel, type, interval):
        """get edge channel.

        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        edge_channel
            {MVH, MVE, MVD, etc}
        """
        edge_interval_code = self._get_interval_code(interval)
        edge_channel = None
        if channel == 'D':
            edge_channel = edge_interval_code + 'VD'
        elif channel == 'E':
            edge_channel = edge_interval_code + 'VE'
        elif channel == 'F':
            edge_channel = edge_interval_code + 'SF'
        elif channel == 'H':
            edge_channel = edge_interval_code + 'VH'
        elif channel == 'Z':
            edge_channel = edge_interval_code + 'VZ'
        else:
            raise TimeseriesFactoryException(
                'Unexpected channel code "%s"' % channel)
        return edge_channel

    def _get_edge_location(self, observatory, channel, type, interval):
        """get edge location.

        The edge location code is currently determined by the type
            passed in.

        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        location
            returns an edge location code
        """
        location = None
        if type == 'variation':
            location = 'R0'
        elif type == 'quasi-definitive':
            location = 'Q0'
        elif type == 'definitive':
            location = 'D0'
        return location

    def _get_interval_code(self, interval):
        """get edge interval code.

        Converts the metadata interval string, into an edge single character
            edge code.

        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        interval type
        """
        interval_code = None
        if interval == 'daily':
            interval_code = 'D'
        elif interval == 'hourly':
            interval_code = 'H'
        elif interval == 'minute':
            interval_code = 'M'
        elif interval == 'second':
            interval_code = 'S'
        else:
            raise TimeseriesFactoryException(
                    'Unexpected interval "%s"' % interval)
        return interval_code

    def _get_timeseries(self, starttime, endtime, observatory,
                channel, type, interval):
        """get timeseries data for a single channel.

        Parameters
        ----------
        starttime: obspy.core.UTCDateTime
            the starttime of the requested data
        endtime: obspy.core.UTCDateTime
            the endtime of the requested data
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        obspy.core.trace
            timeseries trace of the requested channel data
        """
        station = self._get_edge_station(observatory, channel,
                type, interval)
        location = self._get_edge_location(observatory, channel,
                type, interval)
        network = self._get_edge_network(observatory, channel,
                type, interval)
        edge_channel = self._get_edge_channel(observatory, channel,
                type, interval)
        data = self.client.getWaveform(network, station, location,
                edge_channel, starttime, endtime)
        data.merge()
        self._convert_trace_to_decimal(data)
        self._set_metadata(data,
                observatory, channel, type, interval)
        return data

    def _clean_timeseries(self, timeseries, starttime, endtime):
        """Realigns timeseries data so the start and endtimes are the same
            as what was originally asked for, even if the data was during
            a gap.

        Parameters
        ----------
        timeseries: obspy.core.stream
            The timeseries stream as returned by the call to getWaveform
        starttime: obspy.core.UTCDateTime
            the starttime of the requested data
        endtime: obspy.core.UTCDateTime
            the endtime of the requested data

        Notes: the original timeseries object is changed.
        """
        for trace in timeseries:
            trace_starttime = UTCDateTime(trace.stats.starttime)
            trace_endtime = UTCDateTime(trace.stats.endtime)

            if trace.stats.starttime > starttime:
                cnt = int((trace_starttime - starttime) / trace.stats.delta)
                trace.data = numpy.concatenate([
                        numpy.full(cnt, numpy.nan, dtype=numpy.float64),
                        trace.data])
                trace.stats.starttime = starttime
            if trace_endtime < endtime:
                cnt = int((endtime - trace_endtime) / trace.stats.delta)
                trace.data = numpy.concatenate([
                        trace.data,
                        numpy.full(cnt, numpy.nan, dtype=numpy.float64)])
                trace.stats.endttime = endtime

    def _post_process(self, timeseries, starttime, endtime, channels):
        """Post process a timeseries stream after the raw data is
                is fetched from a waveserver. Specifically changes
                any MaskedArray to a ndarray with nans representing gaps.
                Then calls _clean_timeseries to deal with gaps at the
                beggining or end of the streams.

        Parameters
        ----------
        timeseries: obspy.core.stream
            The timeseries stream as returned by the call to getWaveform
        starttime: obspy.core.UTCDateTime
            the starttime of the requested data
        endtime: obspy.core.UTCDateTime
            the endtime of the requested data
        channels: array_like
            list of channels to load

        Notes: the original timeseries object is changed.
        """
        for trace in timeseries:
            if isinstance(trace.data, numpy.ma.MaskedArray):
                trace.data.set_fill_value(numpy.nan)
                trace.data = trace.data.filled()

        self._clean_timeseries(timeseries, starttime, endtime)
        # TODO add in test for missing channel,  if so,  make it all nans?

    def _set_metadata(self, stream, observatory, channel, type, interval):
        """set metadata for a given stream/channel
        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            edge channel code {MVH, MVE, MVD, ...}
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {minute, second}
        """

        for trace in stream:
            self.observatoryMetadata.set_metadata(trace.stats, observatory,
                    channel, type, interval)
