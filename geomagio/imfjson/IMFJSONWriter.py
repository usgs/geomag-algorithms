from __future__ import absolute_import

from collections import OrderedDict
from io import BytesIO
from datetime import datetime
import json
import numpy as np
from .. import ChannelConverter, TimeseriesUtility
from ..TimeseriesFactoryException import TimeseriesFactoryException


class IMFJSONWriter(object):
    """JSON writer.
    """

    def write(self, out, timeseries, channels, url=None):
        """Write timeseries to json file.

        Parameters
        ----------
        out: file object
            file object to be written to. could be stdout
        timeseries: obspy.core.stream
            timeseries object with data to be written
        channels: array_like
            channels to be written from timeseries object
        url: str
            string with the requested url

        Raises
        ------
        TimeseriesFactoryException
            if there is a missing channel.
        """
        file_dict = OrderedDict()
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s'
                    % (channel, str(TimeseriesUtility.get_channels(timeseries)))
                )
        stats = timeseries[0].stats
        file_dict["type"] = "Timeseries"
        file_dict["metadata"] = self._format_metadata(stats, channels)
        file_dict["metadata"]["url"] = url
        file_dict["times"] = self._format_times(timeseries, channels)
        file_dict["values"] = self._format_data(timeseries, channels, stats)
        formatted_timeseries = json.dumps(
            file_dict, ensure_ascii=True, separators=(",", ":")
        ).encode("utf8")
        out.write(formatted_timeseries)

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
        values = []
        for c in channels:
            value_dict = OrderedDict()
            trace = timeseries.select(channel=c)[0]
            value_dict["id"] = c
            value_dict["metadata"] = OrderedDict()
            metadata = value_dict["metadata"]
            metadata["element"] = c
            metadata["network"] = stats.network
            metadata["station"] = stats.station
            edge_channel = trace.stats.channel
            metadata["channel"] = edge_channel
            if stats.location == "":
                if stats.data_type == "variation" or stats.data_type == "reported":
                    stats.location = "R0"
                elif stats.data_type == "adjusted" or stats.data_type == "provisional":
                    stats.location = "A0"
                elif stats.data_type == "quasi-definitive":
                    stats.location = "Q0"
                elif stats.data_type == "definitive":
                    stats.location = "D0"
            metadata["location"] = stats.location
            values += [value_dict]
            series = np.copy(trace.data)
            if c == "D":
                series = ChannelConverter.get_minutes_from_radians(series)
            # Converting numpy array to list required for JSON serialization
            series = series.tolist()
            series = [None if str(x) == "nan" else x for x in series]
            value_dict["values"] = series
            # TODO: Add flag metadata
        return values

    def _format_metadata(self, stats, channels):
        """Format metadata for json file and update dictionary

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
        imo["iaga_code"] = stats.station
        if "station_name" in stats:
            imo["name"] = stats.station_name
        coords = [None] * 3
        if "geodetic_longitude" in stats:
            coords[0] = float(stats.geodetic_longitude)
        if "geodetic_latitude" in stats:
            coords[1] = float(stats.geodetic_latitude)
        try:
            if "elevation" in stats:
                coords[2] = float(stats.elevation)
        except (KeyError, ValueError, TypeError):
            pass
        imo["coordinates"] = coords
        intermag["imo"] = imo
        intermag["reported_orientation"] = "".join(channels)
        if "sensor_orientation" in stats:
            intermag["sensor_orientation"] = stats.sensor_orientation
        if "data_type" in stats:
            intermag["data_type"] = stats.data_type
        if "sampling_rate" in stats:
            if stats.sampling_rate == 1.0 / 60.0:
                rate = 60
            elif stats.sampling_rate == 1.0 / 3600.0:
                rate = 3600
            elif stats.sampling_rate == 1.0 / 86400.0:
                rate = 86400
            else:
                rate = 1
            intermag["sampling_period"] = rate
        # 1/sampling_rate to output in seconds rather than hertz
        if "sensor_sampling_rate" in stats:
            sampling = 1 / stats.sensor_sampling_rate
            intermag["digital_sampling_rate"] = sampling
        metadata_dict["intermagnet"] = intermag
        metadata_dict["status"] = 200
        generated = datetime.utcnow()
        metadata_dict["generated"] = generated.strftime("%Y-%m-%dT%H:%M:%SZ")
        return metadata_dict

    def _format_times(self, timeseries, channels):
        """Format times for json file and update dictionary

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces with channel listed in channels
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
            times.append(
                self._format_time_string(
                    datetime.utcfromtimestamp(starttime + i * delta)
                )
            )
        return times

    def _format_time_string(self, time):
        """Format one datetime object.

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
        return (
            "{0.tm_year:0>4d}-{0.tm_mon:0>2d}-{0.tm_mday:0>2d}T"
            "{0.tm_hour:0>2d}:{0.tm_min:0>2d}:{0.tm_sec:0>2d}.{1:0>3d}Z"
            "".format(tt, int(time.microsecond / 1000))
        )

    @classmethod
    def format(self, timeseries, channels, url=None):
        """Get a json formatted string.

        Calls write() with a BytesIO, and returns the output.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces with channel listed in channels
        channels: array_like
            channels to be written from timeseries
        url: str
            string with the requested url

        Returns
        -------
        unicode
         json formatted string.
        """
        out = BytesIO()
        writer = IMFJSONWriter()
        writer.write(out, timeseries, channels, url=url)
        return out.getvalue()
