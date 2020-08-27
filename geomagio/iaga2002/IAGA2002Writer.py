from __future__ import absolute_import
from builtins import range

from io import BytesIO
from datetime import datetime
import numpy
from os import linesep
import textwrap
from .. import ChannelConverter, TimeseriesUtility
from ..TimeseriesFactoryException import TimeseriesFactoryException
from ..Util import create_empty_trace
from . import IAGA2002Parser


class IAGA2002Writer(object):
    """IAGA2002 writer."""

    def __init__(
        self,
        empty_value=IAGA2002Parser.NINES,
        empty_channel=IAGA2002Parser.EMPTY_CHANNEL,
    ):
        self.empty_value = empty_value
        self.empty_channel = empty_channel

    def write(self, out, timeseries, channels):
        """write timeseries to iaga file

        Parameters
        ----------
        out: file object
            file object to be written to. could be stdout
        timeseries: obspy.core.stream
            timeseries object with data to be written
        channels: array_like
            channels to be written from timeseries object
        """
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s'
                    % (channel, str(TimeseriesUtility.get_channels(timeseries)))
                )
        stats = timeseries[0].stats
        if len(channels) != 4:
            channels = self._pad_to_four_channels(timeseries, channels)
        out.write(self._format_headers(stats, channels).encode("utf8"))
        out.write(self._format_comments(stats).encode("utf8"))
        out.write(self._format_channels(channels, stats.station).encode("utf8"))
        out.write(self._format_data(timeseries, channels).encode("utf8"))

    def _format_headers(self, stats, channels):
        """format headers for IAGA2002 file

        Parameters
        ----------
        stats: obspy.core.trace.stats
            holds the observatory metadata
        channels: array_like
            channels to be reported.

        Returns
        -------
        array_like
            an array containing formatted strings of header data.
        """
        buf = []
        buf.append(self._format_header("Format", "IAGA-2002"))
        if "agency_name" in stats:
            buf.append(self._format_header("Source of Data", stats.agency_name))
        if "station_name" in stats:
            buf.append(self._format_header("Station Name", stats.station_name))
        buf.append(self._format_header("IAGA CODE", stats.station))
        if "geodetic_latitude" in stats:
            buf.append(
                self._format_header("Geodetic Latitude", str(stats.geodetic_latitude))
            )
        if "geodetic_longitude" in stats:
            buf.append(
                self._format_header("Geodetic Longitude", str(stats.geodetic_longitude))
            )
        if "elevation" in stats:
            buf.append(self._format_header("Elevation", stats.elevation))
        buf.append(self._format_header("Reported", "".join(channels)))
        if "sensor_orientation" in stats:
            buf.append(
                self._format_header("Sensor Orientation", stats.sensor_orientation)
            )
        if "sensor_sampling_rate" in stats:
            buf.append(
                self._format_header(
                    "Digital Sampling", str(1 / stats.sensor_sampling_rate) + " second"
                )
            )
        if "data_interval_type" in stats:
            buf.append(
                self._format_header("Data Interval Type", stats.data_interval_type)
            )
        if "data_type" in stats:
            buf.append(self._format_header("Data Type", stats.data_type))
        return "".join(buf)

    def _format_comments(self, stats):
        """format comments for IAGA2002 file

        Parameters
        ----------
        stats: obspy.core.trace.stats
            holds the observatory metadata

        Returns
        -------
        array_like
            an array containing formatted strings of header data.
        """
        comments = []
        if (
            "declination_base" in stats
            and stats.declination_base is not None
            and (stats.data_type == "variation" or stats.data_type == "reported")
        ):
            comments.append(
                "DECBAS               {:<8d}"
                "(Baseline declination value in tenths of minutes East"
                " (0-216,000)).".format(stats.declination_base)
            )
        if "filter_comments" in stats:
            comments.extend(stats.filter_comments)
        if "comments" in stats:
            comments.extend(stats.comments)
        if "is_gin" in stats and stats.is_gin:
            comments.append("This data file was constructed by the Golden " + "GIN.")
        if "is_intermagnet" in stats and stats.is_intermagnet:
            comments.append("Final data will be available on the" + " INTERMAGNET DVD.")
            comments.append(
                "Go to www.intermagnet.org for details on" + " obtaining this product."
            )
        if "conditions_of_use" in stats and stats.conditions_of_use is not None:
            comments.append("CONDITIONS OF USE: " + stats.conditions_of_use)
        # generate comment output
        buf = []
        for comment in comments:
            buf.append(self._format_comment(comment))
        return "".join(buf)

    def _format_header(self, name, value):
        """format headers for IAGA2002 file

        Parameters
        ----------
        name: str
            the name to be written
        value: str
            the value to written.

        Returns
        -------
        str
            a string formatted to be a single header line in an IAGA2002 file
        """
        prefix = " "
        suffix = " |" + linesep
        return "".join((prefix, name.ljust(23), value.ljust(44), suffix))

    def _format_comment(self, comment):
        """format header for IAGA2002 file

        Parameters
        ----------
        comment: str
            a single comment to be broken formatted if needed.
        Returns
        -------
        str
            a string formatted to be a single comment in an IAGA2002 file.
        """
        buf = []
        prefix = " # "
        suffix = " |" + linesep
        lines = textwrap.wrap(comment, 65)
        for line in lines:
            buf.extend((prefix, line.ljust(65), suffix))
        return "".join(buf)

    def _format_channels(self, channels, iaga_code):
        """Format channel header line.

        Parameters
        ----------
        channels : sequence
            list and order of channel values to output.
        iaga_code : str
            observatory code, which is prefixed to channel name in output.

        Returns
        -------
        str
            Channel header line as a string (including newline)
        """
        iaga_code_len = len(iaga_code)
        if iaga_code_len != 3 and iaga_code_len != 4:
            raise TimeseriesFactoryException(
                'iaga_code "{}" is not 3 characters'.format(iaga_code)
            )
        if len(channels) != 4:
            raise TimeseriesFactoryException("more than 4 channels {}".format(channels))
        buf = ["DATE       TIME         DOY  "]
        for channel in channels:
            channel_len = len(channel)
            if channel_len < 1 or channel_len > 4:
                raise TimeseriesFactoryException(
                    'channel "{}" is not 1 character'.format(channel)
                )
            buf.append("   {:<7s}".format(iaga_code + channel))
        buf.append("|" + linesep)
        return "".join(buf)

    def _format_data(self, timeseries, channels):
        """Format all data lines.

        Parameters
        ----------
        timeseries : obspy.core.Stream
            stream containing traces with channel listed in channels
        channels : sequence
            list and order of channel values to output.
        """
        buf = []
        if timeseries.select(channel="D"):
            d = timeseries.select(channel="D")
            d[0].data = ChannelConverter.get_minutes_from_radians(d[0].data)
        traces = [timeseries.select(channel=c)[0] for c in channels]
        starttime = float(traces[0].stats.starttime)
        delta = traces[0].stats.delta
        for i in range(len(traces[0].data)):
            buf.append(
                self._format_values(
                    datetime.utcfromtimestamp(starttime + i * delta),
                    (t.data[i] for t in traces),
                )
            )
        return "".join(buf)

    def _format_values(self, time, values):
        """Format one line of data values.

        Parameters
        ----------
        time : datetime
            timestamp for values
        values : sequence
            list and order of channel values to output.
            if value is NaN, self.empty_value is output in its place.

        Returns
        -------
        unicode
            Formatted line containing values.
        """
        tt = time.timetuple()
        return (
            "{0.tm_year:0>4d}-{0.tm_mon:0>2d}-{0.tm_mday:0>2d} "
            "{0.tm_hour:0>2d}:{0.tm_min:0>2d}:{0.tm_sec:0>2d}.{1:0>3d} "
            "{0.tm_yday:0>3d}   "
            " {2:9.2f} {3:9.2f} {4:9.2f} {5:9.2f}".format(
                tt,
                int(time.microsecond / 1000),
                *[self.empty_value if numpy.isnan(val) else val for val in values]
            )
            + linesep
        )

    def _pad_to_four_channels(self, timeseries, channels):
        padded = channels[:]
        for x in range(len(channels), 4):
            channel = self.empty_channel
            padded.append(channel)
            timeseries += create_empty_trace(timeseries[0], channel)
        return padded

    @classmethod
    def format(self, timeseries, channels):
        """Get an IAGA2002 formatted string.

        Calls write() with a BytesIO, and returns the output.

        Parameters
        ----------
        timeseries : obspy.core.Stream

        Returns
        -------
        unicode
          IAGA2002 formatted string.
        """
        out = BytesIO()
        writer = IAGA2002Writer()
        writer.write(out, timeseries, channels)
        return out.getvalue()
