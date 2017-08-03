from __future__ import absolute_import
from builtins import range

from io import BytesIO
from collections import OrderedDict
from datetime import datetime
import json
import numpy
import textwrap
from .. import ChannelConverter, TimeseriesUtility
from ..edge import EdgeFactory
from ..TimeseriesFactoryException import TimeseriesFactoryException
from ..Util import create_empty_trace


class JSONWriter(object):
    """JSON writer.
    """

    def __init__(self):
        self.dictionary = OrderedDict()

    def write(self, out, timeseries, channels, **kwargs):
        """write timeseries to json file

        Parameters
        ----------
        out: file object
            file object to be written to. could be stdout
        timeseries: obspy.core.stream
            timeseries object with data to be written
        channels: array_like
            channels to be written from timeseries object
        """
        request = kwargs.get('request')
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s' %
                    (channel, str(TimeseriesUtility.get_channels(timeseries))))
        stats = timeseries[0].stats
        if len(channels) != 4:
            channels = self._pad_to_four_channels(timeseries, channels)
        self._format_metadata(stats, channels)
        if request:
            self.dictionary['metadata']['url'] = 'http://geomag.usgs.gov/ws/edge/?' + request
        self._format_times(timeseries, channels)
        self._format_data(timeseries, channels, stats)
        out.write(json.dumps(self.dictionary, ensure_ascii=True).encode(
                'utf8'))

    def _format_metadata(self, stats, channels):
        """format metadata for json file and update dictionary

        Parameters
        ----------
        stats: obspy.core.trace.stats
            holds the observatory metadata
        channels: array_like
            channels to be reported.
        """
        dict = self.dictionary.copy()
        dict['type'] = 'Timeseries'
        dict['metadata'] = OrderedDict()
        dict['metadata']['intermagnet'] = OrderedDict()
        dict['metadata']['intermagnet']['imo'] = OrderedDict()
        dict['metadata']['intermagnet']['imo']['iaga_code'] = stats.station
        if 'station_name' in stats:
            dict['metadata']['intermagnet']['imo']['name'] = stats.station_name
        coords = [None] * 3
        if 'geodetic_longitude' in stats:
            coords[0] = str(stats.geodetic_longitude)
        if 'geodetic_latitude' in stats:
            coords[1] = str(stats.geodetic_latitude)
        if 'elevation' in stats:
            coords[2] = str(stats.elevation)
        dict['metadata']['intermagnet']['imo']['coordinates'] = coords
        dict['metadata']['intermagnet']['reported_orientation'] = ''.join(channels)
        if 'sensor_orientation' in stats:
            dict['metadata']['intermagnet']['sensor_orientation'] = stats.sensor_orientation
        if 'data_type' in stats:
            dict['metadata']['intermagnet']['data_type'] = stats.data_type
        if 'sampling_rate' in stats:
            if stats.sampling_rate == 1. / 60.:
                rate = 60
            elif stats.sampling_rate == 1. / 3600.:
                rate = 3600
            elif stats.sampling_rate == 1. / 86400.:
                rate = 86400
            else:
                rate = 1
            dict['metadata']['intermagnet']['sampling_period'] = str(rate)
        if 'sensor_sampling_rate' in stats:
            dict['metadata']['intermagnet']['digital_sampling_rate'] = str(1 / stats.sensor_sampling_rate)
        dict['metadata']['status'] = 200
        dict['metadata']['generated'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.dictionary = dict

    def _format_times(self, timeseries, channels):
        """format times for json file and update dictionary

        Parameters
        ----------
        timeseries: obspy.core.stream
            timeseries object with data to be written
        channels: array_like
            channels to be reported.
        """
        times = []
        traces = [timeseries.select(channel=c)[0] for c in channels]
        starttime = float(traces[0].stats.starttime)
        delta = traces[0].stats.delta
        for i in range(len(traces[0].data)):
            times.append(self._format_time_string(
                datetime.utcfromtimestamp(starttime + i * delta)))
        self.dictionary['times'] = times

    def _format_time_string(self, time):
        """format one time.

        Parameters
        ----------
        time : datetime
            timestamp for values

        Returns
        -------
        unicode
            formatted time.
        """
        tt = time.timetuple()
        return '{0.tm_year:0>4d}-{0.tm_mon:0>2d}-{0.tm_mday:0>2d}T' \
                '{0.tm_hour:0>2d}:{0.tm_min:0>2d}:{0.tm_sec:0>2d}.{1:0>3d}Z'.format(
                tt, int(time.microsecond / 1000))

    def _format_data(self, timeseries, channels, stats):
        """Format all data lines.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces with channel listed in channels
        channels : sequence
            list and order of channel values to output.
        stats: obspy.core.trace.stats
            holds the observatory metadata
        """
        self.dictionary['values'] = []
        if timeseries.select(channel='D'):
            d = timeseries.select(channel='D')
            d[0].data = ChannelConverter.get_minutes_from_radians(d[0].data)
        values = []
        self.edge = EdgeFactory()
        for c in channels:
            value_dict = OrderedDict()
            trace = timeseries.select(channel=c)[0]
            value_dict['id'] = c
            value_dict['metadata'] = OrderedDict()
            value_dict['metadata']['element'] = c
            if 'network' in stats:
                value_dict['metadata']['network'] = stats.network
            value_dict['metadata']['station'] = stats.station
            edge_channel = self.edge._get_edge_channel(stats.station,
                                                        c,
                                                        stats.data_type,
                                                        stats.data_interval)
            value_dict['metadata']['channel'] = edge_channel
            if 'location' in stats:
                value_dict['metadata']['location'] = stats.location
            # TODO: Add flag metadata
            values += [value_dict]
            data = []
            for i in range(len(trace.data)):
                if numpy.isnan(trace.data[i]):
                    data += ['null']
                else:
                    data += [str(trace.data[i])]


            value_dict['values'] = data
        self.dictionary['values'] += values

    def _pad_to_four_channels(self, timeseries, channels):
        padded = channels[:]
        for x in range(len(channels), 4):
            channel = 'NUL'
            padded.append(channel)
            timeseries += create_empty_trace(timeseries[0], channel)
        return padded

    @classmethod
    def format(self, timeseries, channels, **kwargs):
        """Get a json formatted string.

        Calls write() with a BytesIO, and returns the output.

        Parameters
        ----------
        kwargs
            request : query string
        timeseries : obspy.core.Stream

        Returns
        -------
        unicode
         json formatted string.
        """
        request = kwargs.get('request')
        out = BytesIO()
        writer = JSONWriter()
        writer.write(out, timeseries, channels, request)
        return out.getvalue()
