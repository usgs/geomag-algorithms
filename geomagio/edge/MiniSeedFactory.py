"""Factory that loads data from earthworm and writes to Edge.

EdgeFactory uses obspy earthworm class to read data from any
earthworm standard Waveserver using the obspy getWaveform call.

Writing will be implemented with Edge specific capabilities,
to take advantage of it's newer realtime abilities.

Edge is the USGS earthquake hazard centers replacement for earthworm.
"""
from __future__ import absolute_import

import sys
import numpy
import numpy.ma

import obspy.core
from obspy.clients.neic import client as miniseed

from .. import ChannelConverter, TimeseriesUtility
from ..Metadata import get_instrument
from ..TimeseriesFactory import TimeseriesFactory
from ..TimeseriesFactoryException import TimeseriesFactoryException
from ..ObservatoryMetadata import ObservatoryMetadata
from .MiniSeedInputClient import MiniSeedInputClient


class MiniSeedFactory(TimeseriesFactory):
    """TimeseriesFactory for Edge related data.

    Parameters
    ----------
    host: str
        a string representing the IP number of the host to connect to.
    port: integer
        the port number the miniseed query server is listening on.
    observatory: str
        the observatory code for the desired observatory.
    channels: array
        an array of channels {H, D, E, F, Z, MGD, MSD, HGD}.
        Known since channel names are mapped based on interval and type,
        others are passed through, see #_get_edge_channel().
    type: str
        the data type {variation, quasi-definitive, definitive}
    interval: str
        the data interval {'day', 'hour', 'minute', 'second', 'tenhertz'}
    observatoryMetadata: ObservatoryMetadata object
        an ObservatoryMetadata object used to replace the default
        ObservatoryMetadata.
    locationCode: str
        the location code for the given edge server, overrides type
        in get_timeseries/put_timeseries

    See Also
    --------
    TimeseriesFactory

    Notes
    -----
    This is designed to read from any earthworm style waveserver, but it
        currently only writes to an edge. Edge mimics an earthworm style
        waveserver close enough that we hope to maintain that compatibility
        for reading.
    """

    def __init__(
        self,
        host="cwbpub.cr.usgs.gov",
        port=2061,
        write_port=7981,
        observatory=None,
        channels=None,
        type=None,
        interval=None,
        observatoryMetadata=None,
        locationCode=None,
        convert_channels=None,
    ):
        TimeseriesFactory.__init__(self, observatory, channels, type, interval)

        self.client = miniseed.Client(host, port)
        self.observatoryMetadata = observatoryMetadata or ObservatoryMetadata()
        self.locationCode = locationCode
        self.interval = interval
        self.host = host
        self.port = port
        self.write_port = write_port
        self.convert_channels = convert_channels or []
        self.write_client = MiniSeedInputClient(self.host, self.write_port)

    def get_timeseries(
        self,
        starttime,
        endtime,
        observatory=None,
        channels=None,
        type=None,
        interval=None,
    ):
        """Get timeseries data

        Parameters
        ----------
        starttime: obspy.core.UTCDateTime
            time of first sample.
        endtime: obspy.core.UTCDateTime
            time of last sample.
        observatory: str
            observatory code.
        channels: array_like
            list of channels to load
        type: {'variation', 'quasi-definitive', 'definitive'}
            data type.
        interval: {'day', 'hour', 'minute', 'second', 'tenhertz'}
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
                'Starttime before endtime "%s" "%s"' % (starttime, endtime)
            )

        # obspy factories sometimes write to stdout, instead of stderr
        original_stdout = sys.stdout
        try:
            # send stdout to stderr
            sys.stdout = sys.stderr
            # get the timeseries
            timeseries = obspy.core.Stream()
            for channel in channels:
                if channel in self.convert_channels:
                    data = self._convert_timeseries(
                        starttime, endtime, observatory, channel, type, interval
                    )
                else:
                    data = self._get_timeseries(
                        starttime, endtime, observatory, channel, type, interval
                    )
                timeseries += data
        finally:
            # restore stdout
            sys.stdout = original_stdout

        self._post_process(timeseries, starttime, endtime, channels)
        return timeseries

    def put_timeseries(
        self,
        timeseries,
        starttime=None,
        endtime=None,
        observatory=None,
        channels=None,
        type=None,
        interval=None,
    ):
        """Put timeseries data

        Parameters
        ----------
        timeseries: obspy.core.Stream
            timeseries object with data to be written
        observatory: str
            observatory code.
        channels: array_like
            list of channels to load
        type: {'variation', 'quasi-definitive', 'definitive'}
            data type.
        interval: {'day', 'hour', 'minute', 'second', 'tenhertz'}
            data interval.

        Notes
        -----
        Streams sent to timeseries are expected to have a single trace per
            channel and that trace should have an ndarray, with nan's
            representing gaps.
        """
        stats = timeseries[0].stats
        observatory = observatory or stats.station or self.observatory
        channels = channels or self.channels
        type = type or self.type or stats.data_type
        interval = interval or self.interval or stats.data_interval

        if starttime is None or endtime is None:
            starttime, endtime = TimeseriesUtility.get_stream_start_end_times(
                timeseries
            )
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s'
                    % (channel, str(TimeseriesUtility.get_channels(timeseries)))
                )
        for channel in channels:
            self._put_channel(
                timeseries, observatory, channel, type, interval, starttime, endtime
            )
        # close socket
        self.write_client.close()

    def get_calculated_timeseries(
        self, starttime, endtime, observatory, channel, type, interval, components
    ):
        """Calculate a single channel using multiple component channels.

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
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}
        components: list
            each component is a dictionary with the following keys:
                channel: str
                offset: float
                scale: float

        Returns
        -------
        obspy.core.trace
            timeseries trace of the converted channel data
        """
        # sum channels
        stats = None
        converted = None
        for component in components:
            # load component
            data = self._get_timeseries(
                starttime, endtime, observatory, component["channel"], type, interval
            )[0]
            # convert to nT
            nt = data.data * component["scale"] + component["offset"]
            # add to converted
            if converted is None:
                converted = nt
                stats = obspy.core.Stats(data.stats)
            else:
                converted += nt
        # set channel parameter to U, V, or W
        stats.channel = channel
        # create empty trace with adapted stats
        out = TimeseriesUtility.create_empty_trace(
            stats.starttime,
            stats.endtime,
            stats.station,
            stats.channel,
            stats.data_type,
            stats.data_interval,
            stats.network,
            stats.station,
            stats.location,
        )
        out.data = converted
        return out

    def _convert_stream_to_masked(self, timeseries, channel):
        """convert geomag edge traces in a timeseries stream to a MaskedArray
            This allows for gaps and splitting.
        Parameters
        ----------
        stream : obspy.core.stream
            a stream retrieved from a geomag edge representing one channel.
        channel: string
            the channel to be masked.
        Returns
        -------
        obspy.core.stream
            a stream with all traces converted to masked arrays.
        """
        stream = timeseries.copy()
        for trace in stream.select(channel=channel):
            trace.data = numpy.ma.masked_invalid(trace.data)
        return stream

    def _get_edge_channel(self, observatory, channel, type, interval):
        """get edge channel.

        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F, X, Y, G} or
            any appropriate edge channel, ie MSD, MGD, HGD.
        type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}

        Returns
        -------
        edge_channel
            {MVH, MVE, MVD, MGD etc}
        """
        edge_interval_code = self._get_interval_code(interval)
        edge_channel = None

        # If form is chan.loc, return chan (left) portion.
        # Allows specific chan/loc selection.
        if channel.find(".") >= 0:
            tmplist = channel.split(".")
            return tmplist[0].strip()

        # see if channel name uses _ for ELEMENT_SUFFIX
        element = None
        suffix = None
        if channel.find("_") >= 0:
            element, suffix = channel.split("_")

        # 10Hz should be bin/volt
        if interval == "tenhertz":
            middle = None
            if suffix == "Bin":
                middle = "Y"
            elif suffix == "Volt":
                middle = "E"
            elif suffix is not None:
                raise TimeseriesFactoryException(
                    'bad channel suffix "%s", wanted "Bin" or "Volt"' % suffix
                )
            # check for expected channels
            if element in ("U", "V", "W") and middle is not None:
                return edge_interval_code + middle + element
            else:
                # unknown, assume advanced user
                return channel

        if suffix is not None:
            if suffix == "Dist" or suffix == "SQ" or suffix == "SV" or suffix == "DT":
                # these suffixes modify location code, but use element channel
                channel = element
            else:
                raise TimeseriesFactoryException(
                    'bad channel suffix "%s", wanted "Dist", "SQ", or "SV"' % suffix
                )
        if channel in ("D", "F", "G", "H", "U", "V", "W", "X", "Y", "Z"):
            # normal elements
            edge_channel = edge_interval_code + "F" + channel
        elif channel == "E-E":
            edge_channel = edge_interval_code + "QE"
        elif channel == "E-N":
            edge_channel = edge_interval_code + "QN"
        elif channel == "Dst4":
            edge_channel = edge_interval_code + "X4"
        elif channel == "Dst3":
            edge_channel = edge_interval_code + "X3"
        else:
            edge_channel = channel
        return edge_channel

    def _get_edge_location(self, observatory, channel, data_type, interval):
        """get edge location.

        The edge location code is currently determined by the type
            passed in.

        Parameters
        ----------
        observatory : str
            observatory code
        channel : str
            single character channel {H, E, D, Z, F}
        data_type : str
            data type {definitive, quasi-definitive, variation}
        interval : str
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}

        Returns
        -------
        location
            returns an edge location code
        """
        # If form is chan.loc, return loc (right) portion
        # Allows specific chan/loc selection.
        if channel.find(".") >= 0:
            tmplist = channel.split(".")
            return tmplist[1].strip()
        # factory override
        if self.locationCode is not None:
            return self.locationCode
        # determine prefix
        location_prefix = "R"
        if data_type == "variation" or data_type == "reported":
            location_prefix = "R"
        elif data_type == "adjusted" or data_type == "provisional":
            location_prefix = "A"
        elif data_type == "quasi-definitive":
            location_prefix = "Q"
        elif data_type == "definitive":
            location_prefix = "D"
        # determine suffix
        location_suffix = "0"
        if channel.find("_") >= 0:
            _, suffix = channel.split("_")
            if suffix == "Dist":
                location_suffix = "D"
            elif suffix == "SQ":
                location_suffix = "Q"
            elif suffix == "SV":
                location_suffix = "V"
            elif suffix == "DT":
                location_suffix = "R"
            elif suffix not in ("Bin", "Volt"):
                raise TimeseriesFactoryException(
                    'bad channel suffix "%s", wanted "Dist", "SQ", or "SV"' % suffix
                )
        return location_prefix + location_suffix

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
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}

        Returns
        -------
        network
            always NT
        """
        return "NT"

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
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}

        Returns
        -------
        station
            the observatory is returned as the station
        """
        return observatory

    def _get_interval_code(self, interval):
        """get edge interval code.

        Converts the metadata interval string, into an edge single character
            edge code.

        Parameters
        ----------
        interval : str
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}

        Returns
        -------
        interval type
        """
        interval_code = None
        if interval == "day":
            interval_code = "P"
        elif interval == "hour":
            interval_code = "R"
        elif interval == "minute":
            interval_code = "U"
        elif interval == "second":
            interval_code = "L"
        elif interval == "tenhertz":
            interval_code = "B"
        else:
            raise TimeseriesFactoryException('Unexpected interval "%s"' % interval)
        return interval_code

    def _get_timeseries(self, starttime, endtime, observatory, channel, type, interval):
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
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}

        Returns
        -------
        obspy.core.trace
            timeseries trace of the requested channel data
        """
        station = self._get_edge_station(observatory, channel, type, interval)
        location = self._get_edge_location(observatory, channel, type, interval)
        network = self._get_edge_network(observatory, channel, type, interval)
        edge_channel = self._get_edge_channel(observatory, channel, type, interval)
        data = self.client.get_waveforms(
            network, station, location, edge_channel, starttime, endtime
        )
        data.merge()
        if data.count() == 0:
            data += TimeseriesUtility.create_empty_trace(
                starttime,
                endtime,
                observatory,
                channel,
                type,
                interval,
                network,
                station,
                location,
            )
        self._set_metadata(data, observatory, channel, type, interval)
        return data

    def _convert_timeseries(
        self, starttime, endtime, observatory, channel, type, interval
    ):
        """Generate a single channel using multiple components.

        Finds metadata, then calls _get_converted_timeseries for actual
        conversion.

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
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}

        Returns
        -------
        obspy.core.trace
            timeseries trace of the requested channel data
        """
        out = obspy.core.Stream()
        metadata = get_instrument(observatory, starttime, endtime)
        # loop in case request spans different configurations
        for entry in metadata:
            entry_endtime = entry["end_time"]
            entry_starttime = entry["start_time"]
            instrument = entry["instrument"]
            instrument_channels = instrument["channels"]
            if channel not in instrument_channels:
                # no idea how to convert
                continue
            # determine metadata overlap with request
            start = (
                starttime
                if entry_starttime is None or entry_starttime < starttime
                else entry_starttime
            )
            end = (
                endtime
                if entry_endtime is None or entry_endtime > endtime
                else entry_endtime
            )
            # now convert
            out += self.get_calculated_timeseries(
                start,
                end,
                observatory,
                channel,
                type,
                interval,
                instrument_channels[channel],
            )
        return out

    def _post_process(self, timeseries, starttime, endtime, channels):
        """Post process a timeseries stream after the raw data is
                is fetched from querymom. Specifically changes
                any MaskedArray to a ndarray with nans representing gaps.
                Then calls pad_timeseries to deal with gaps at the
                beggining or end of the streams.

        Parameters
        ----------
        timeseries: obspy.core.stream
            The timeseries stream as returned by the call to get_waveforms
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

        if "D" in channels:
            for trace in timeseries.select(channel="D"):
                trace.data = ChannelConverter.get_radians_from_minutes(trace.data)

        TimeseriesUtility.pad_timeseries(timeseries, starttime, endtime)

    def _put_channel(
        self, timeseries, observatory, channel, type, interval, starttime, endtime
    ):
        """Put a channel worth of data

        Parameters
        ----------
        timeseries: obspy.core.Stream
            timeseries object with data to be written
        observatory: str
            observatory code.
        channel: str
            channel to load
        type: {'variation', 'quasi-definitive', 'definitive'}
            data type.
        interval: {'day', 'hour', 'minute', 'second', 'tenhertz'}
            data interval.
        starttime: obspy.core.UTCDateTime
        endtime: obspy.core.UTCDateTime
        """
        # use separate traces when there are gaps
        to_write = timeseries.select(channel=channel)
        to_write = TimeseriesUtility.mask_stream(to_write)
        to_write = to_write.split()
        to_write = TimeseriesUtility.unmask_stream(to_write)
        # relabel channels from internal to edge conventions
        station = self._get_edge_station(observatory, channel, type, interval)
        location = self._get_edge_location(observatory, channel, type, interval)
        network = self._get_edge_network(observatory, channel, type, interval)
        edge_channel = self._get_edge_channel(observatory, channel, type, interval)
        for trace in to_write:
            trace.stats.station = station
            trace.stats.location = location
            trace.stats.network = network
            trace.stats.channel = edge_channel
        # finally, send to edge
        self.write_client.send(to_write)

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
            interval length {'day', 'hour', 'minute', 'second', 'tenhertz'}
        """

        for trace in stream:
            self.observatoryMetadata.set_metadata(
                trace.stats, observatory, channel, type, interval
            )
