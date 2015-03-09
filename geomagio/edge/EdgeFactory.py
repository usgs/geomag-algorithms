"""Factory that loads data from earthworm and writes to Edge."""

import obspy.core
from geomagio import TimeseriesFactory, TimeseriesFactoryException
from obspy import earthworm
from ObservatoryMetadata import ObservatoryMetadata


class EdgeFactory(TimeseriesFactory):

    def __init__(self, host=None, port=None, observatory=None,
            channels=None, type=None, interval=None, ):
        TimeseriesFactory.__init__(self, observatory, channels, type, interval)
        self.client = earthworm.Client(host, port)

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
        channels = channels or self.channels

        timeseries = None
        for channel in channels:
            data = self._get_timeseries(starttime, endtime, observatory,
                    channel, type, interval)
            if timeseries is None:
                timeseries = data
            else:
                timeseries += data

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
        raise NotImplementedError('"get_timeseries" not implemented')

    def get_edge_channel_codes(self, observatory, channels, type, interval):
        """Get Edge channel(s) codes given single character channel(s)

        Parameters
        ----------
        observatory : str
            observatory code
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        array_like
            list of corresponding edge channel names {MVH, SVH, MVE, SVE, ...}
        """
        earthworm_channels = []
        for channel in channels:
            earthworm_channels.append(self._get_edge_channel(observatory,
                channel, type, interval))
        return earthworm_channels

    def get_interval_from_edge(self, channels):
        """Get interval from edge style channel codes

        Parameters
        ----------
        channels: array_like
            list of edge channel codes (MVH, MVE, etc)

        Returns
        -------
        channels: array_like
            list of channel codes (H, E, D, Z, etc)
        """
        interval = None
        for channel in channels:
            if interval is not None and interval is not channel[0]:
                raise TimeseriesFactoryException(
                    'Mixed interval values"%s" "%s"' % (interval, channel[0]))
            interval = channel[0]
        return self._get_interval_from_code(interval)

    def get_type_from_edge(self, location):
        """Get type from edge location

        Parameters
        ----------
        location: {R0, R1, Q0, D0}
            the edge location code.

        Returns
        -------
        type: {variation, quasi-definitive, definitive}
            the type of data
        """
        type = None
        if 'location' == 'R0' or 'location' == 'R1':
            type = 'variation'
        elif 'location' == 'Q0':
            type = 'quasi-definitive'
        elif 'location' == 'D0':
            type = 'definitive'
        return type

    def get_channel_code_from_edge(self, channel):
        """Get channel code from edge channel code.

        Parameters
        ----------
        channel: str
            An edge style channel code (MVH, MVE, etc)

        Returns
        -------
        channel: str
            A single character channel code (H, E, Z, F, etc)

        Raises
        ------
        TimeseriesFactoryException
            If input channel is invalid.
        """
        if len(channel) == 3:
            code = channel[2]
        else:
            raise TimeseriesFactoryException(
                'Unexpected Edge Channel"%s"' % channel)
        return code

    def _get_edge_network(self, observatory, channel, type, interval):
        """get edge network code.

        Parameters
        ----------
        observatory : str
            observatory code
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
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
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
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
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
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
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
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
        elif type == 'definite':
            location = 'D0'
        return location

    def _get_edge_code_from_channel(self, channel):
        """get edge code from channel.

        The second character of the edge channel code for geomag represents
            the instrument type.  Currently Variometer and Scalar are
            supported.  Which one is currently decided by the channel
            passed in.

        Parameters
        ----------
        observatory : str
            observatory code
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        channel_code
            partial channel code
        """
        edge_channel = None
        if channel == 'D':
            edge_channel = 'VD'
        elif channel == 'E':
            edge_channel = 'VE'
        elif channel == 'F':
            edge_channel = 'SF'
        elif channel == 'H':
            edge_channel = 'VH'
        elif channel == 'Z':
            edge_channel = 'VZ'
        else:
            raise TimeseriesFactoryException(
                'Unexpected channel code "%s"' % channel)
        return edge_channel

    def _get_interval_from_code(self, interval):
        """get interval from edge Code.

        The first character of an Edge code represents the interval.
            Currently minute and second are represented.

        Parameters
        ----------
        observatory : str
            observatory code
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
        interval : str
            interval length {minute, second}

        Returns
        -------
        interval type
        """
        interval_code = None
        if 'M':
            interval_code = 'minute'
        elif 'S':
            interval_code = 'second'
        else:
            raise TimeseriesFactoryException(
                'Unexpected interval code "%s' % interval)
        return interval_code

    def _get_interval_code(self, interval):
        """get edge interval code.

        Converts the metadata interval string, into an edge single character
            edge code.

        Parameters
        ----------
        observatory : str
            observatory code
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
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
        channels : array_like
            list of single character channels {H, E, D, Z, F}
        type : str
            data type {Definitive, Quasi-definitive, Variation}
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
        channel = self._get_edge_channel(observatory, channel,
                type, interval)
        data = self.client.getWaveform(network, station, location,
                channel, starttime, endtime)
        stats = obspy.core.Stats(data[0].stats)
        stats = ObservatoryMetadata().set_metadata(stats, observatory,
                channel, type, interval)
        data[0].stats = stats
        return data
