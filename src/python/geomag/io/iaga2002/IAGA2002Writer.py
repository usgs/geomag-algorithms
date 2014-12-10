
from cStringIO import StringIO
from geomag.io import TimeseriesFactoryException
import numpy
import IAGA2002Parser
import textwrap


class IAGA2002Writer(object):
    """IAGA2002 writer.
    """

    def __init__(self, empty_value=IAGA2002Parser.NINES):
        self.empty_value = empty_value

    def write(self, out, timeseries, channels):
        stats = timeseries[0].stats
        out.write(self._format_headers(stats, channels))
        out.write(self._format_comments(stats.comments))
        out.write(self._format_channels(channels, stats['IAGA CODE']))
        out.write(self._format_data(timeseries, channels))
        pass

    def _format_headers(self, stats, channels):
        values = {}
        values.update(stats)
        values['Format'] = 'IAGA-2002'
        values['Reported'] = ''.join(channels)
        buf = []
        for header in (
                'Format',
                'Source of Data',
                'Station Name',
                'IAGA CODE',
                'Geodetic Latitude',
                'Geodetic Longitude',
                'Elevation',
                'Reported',
                'Sensor Orientation',
                'Digital Sampling',
                'Data Interval Type',
                'Data Type'):
            buf.append(self._format_header(header, values[header]))
        return ''.join(buf)

    def _format_comments(self, comments):
        buf = []
        for comment in comments:
            buf.append(self._format_comment(comment))
        return ''.join(buf)

    def _format_header(self, name, value):
        prefix = ' '
        suffix = ' |\n'
        return ''.join((prefix, name.ljust(23), value.ljust(44), suffix))

    def _format_comment(self, comment):
        buf = []
        prefix = ' # '
        suffix = ' |\n'
        lines = textwrap.wrap(comment, 65)
        for line in lines:
            buf.extend((prefix, line.ljust(65), suffix))
        return ''.join(buf)

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
        if len(iaga_code) != 3:
            raise TimeseriesFactoryException(
                    'iaga_code "{}" is not 3 characters'.format(iaga_code))
        if len(channels) != 4:
            raise TimeseriesFactoryException(
                    'more than 4 channels {}'.format(channels))
        buf = ['DATE       TIME         DOY']
        for channel in channels:
            if len(channel) != 1:
                raise TimeseriesFactoryException(
                        'channel "{}" is not 1 character'.format(channel))
            buf.append('     %s%s ' % (iaga_code, channel))
        buf.append('  |\n')
        return ''.join(buf)

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
        traces = [timeseries.select(channel=c)[0] for c in channels]
        starttime = traces[0].stats.starttime
        delta = traces[0].stats.delta
        for i in xrange(len(traces[0].data)):
            buf.append(self._format_values(
                starttime + i * delta,
                (t.data[i] for t in traces)))
        return ''.join(buf)

    def _format_values(self, time, values):
        """Format one line of data values.

        Parameters
        ----------
        time : UTCDateTime
            timestamp for values
        values : sequence
            list and order of channel values to output.
            if value is NaN, self.empty_value is output in its place.

        Returns
        -------
        unicode
            Formatted line containing values.
        """
        buf = []
        buf.extend((
                time.strftime('%Y-%m-%d %H:%M:%S.'),
                '{:0>3.0f}'.format(round(time.microsecond / 1000, 0)),
                time.strftime(' %j   ')))
        for value in values:
            if numpy.isnan(value):
                value = self.empty_value
            buf.append('{:10.2f}'.format(value))
        buf.append('\n')
        return ''.join(buf)

    @classmethod
    def format(self, timeseries, channels):
        """Get an IAGA2002 formatted string.

        Calls write() with a StringIO, and returns the output.

        Parameters
        ----------
        timeseries : obspy.core.Stream

        Returns
        -------
        unicode
          IAGA2002 formatted string.
        """
        out = StringIO()
        writer = IAGA2002Writer()
        writer.write(out, timeseries, channels)
        return out.getvalue()
