from __future__ import absolute_import
from builtins import range

from io import BytesIO
from collections import OrderedDict
from datetime import datetime
import json
import numpy as np
import textwrap
from .. import ChannelConverter, TimeseriesUtility
from ..edge import EdgeFactory
from ..TimeseriesFactoryException import TimeseriesFactoryException
from ..Util import create_empty_trace

class JSONWriter(object):
    """JSON writer.
    """

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
        dictionary = OrderedDict()
        request = kwargs.get('request')
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s' %
                    (channel, str(TimeseriesUtility.get_channels(timeseries))))
        stats = timeseries[0].stats
        dictionary['type'] = 'Timeseries'
        dictionary['metadata'] = self._format_metadata(stats, channels)
        if request:
            dictionary['metadata']['url'] = 'http://geomag.usgs.gov/ws/edge/?' + request
        dictionary['times'] = self._format_times(timeseries, channels)
        dictionary['values'] = self._format_data(timeseries, channels, stats)
        out.write(json.dumps(dictionary, ensure_ascii=True).encode(
                'utf8'))

    def _format_metadata(self, stats, channels):
        """format metadata for json file and update dictionary

        Parameters
        ----------
        stats: obspy.core.trace.stats
            holds the observatory metadata
        channels: array_like
            channels to be reported.

        Returns
        -------
        dictionary
            a dictionary containing metadata.
        """
        metadata_dict = OrderedDict()
        intermag = OrderedDict()
        imo = OrderedDict()
        imo['iaga_code'] = stats.station
        if 'station_name' in stats:
            imo['name'] = stats.station_name
        coords = [None] * 3
        if 'geodetic_longitude' in stats:
            coords[0] = str(stats.geodetic_longitude)
        if 'geodetic_latitude' in stats:
            coords[1] = str(stats.geodetic_latitude)
        if 'elevation' in stats:
            coords[2] = str(stats.elevation)
        imo['coordinates'] = coords
        intermag['imo'] = imo
        intermag['reported_orientation'] = ''.join(channels)
        if 'sensor_orientation' in stats:
            intermag['sensor_orientation'] = stats.sensor_orientation
        if 'data_type' in stats:
            intermag['data_type'] = stats.data_type
        if 'sampling_rate' in stats:
            if stats.sampling_rate == 1. / 60.:
                rate = 60
            elif stats.sampling_rate == 1. / 3600.:
                rate = 3600
            elif stats.sampling_rate == 1. / 86400.:
                rate = 86400
            else:
                rate = 1
            intermag['sampling_period'] = str(rate)
        if 'sensor_sampling_rate' in stats:
            intermag['digital_sampling_rate'] = str(1 / stats.sensor_sampling_rate)
        metadata_dict['intermagnet'] = intermag
        metadata_dict['status'] = 200
        metadata_dict['generated'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return metadata_dict

    def _format_times(self, timeseries, channels):
        """format times for json file and update dictionary

        Parameters
        ----------
        stats: obspy.core.trace.stats
            holds the observatory metadata
        channels: array_like
            channels to be reported.

        Returns
        -------
        array_like
            an array containing formatted strings of time data.
        """
        times = []
        traces = [timeseries.select(channel=c)[0] for c in channels]
        starttime = float(traces[0].stats.starttime)
        delta = traces[0].stats.delta
        for i in range(len(traces[0].data)):
            times.append(self._format_time_string(
                datetime.utcfromtimestamp(starttime + i * delta)))
        return times

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

        Returns
        -------
        array_like
            an array containing dictionaries of data.
        """
        if timeseries.select(channel='D'):
            d = timeseries.select(channel='D')
            d[0].data = ChannelConverter.get_minutes_from_radians(d[0].data)
        values = []
        self.edge = EdgeFactory()
        for c in channels:
            value_dict = OrderedDict()
            trace = timeseries.select(channel=c)[0]
            value_dict['id'] = c
            value_dict = OrderedDict()
            value_dict['element'] = c
            if 'network' in stats:
                value_dict['network'] = stats.network
            value_dict['station'] = stats.station
            if 'channel' in stats:
                edge_channel = trace.stats.channel
            else:
                edge_channel = c
            value_dict['channel'] = edge_channel
            if 'location' in stats:
                value_dict['location'] = stats.location
            # TODO: Add flag metadata
            values += [value_dict]
            data = np.copy(trace.data)
            data[np.isnan(data)] = None
            value_dict['values'] = data.tolist()
        return values

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
