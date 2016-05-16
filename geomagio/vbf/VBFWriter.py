
import numpy
from cStringIO import StringIO
from datetime import datetime
from .. import ChannelConverter, TimeseriesUtility
from ..TimeseriesFactoryException import TimeseriesFactoryException
from obspy.core import Stream


# For a binlog, need to save previous time and volts.
h_prev = [99.999999, 999]
e_prev = [99.999999, 999]
z_prev = [99.999999, 999]
# Use seperate HEZ buffers to group binlog output by component.
Hbuf = []
Ebuf = []
Zbuf = []


class VBFWriter(object):
    """VBF writer.
    """

    def __init__(self, empty_value=numpy.int('9999999')):
        self.empty_value = empty_value

    def write(self, out, timeseries, channels):
        """Write timeseries to vbf file.

        Parameters
        ----------
            out : file object
                File object to be written to. Could be stdout.
            timeseries : obspy.core.stream
                Timeseries object with data to be written.
            channels : array_like
                Channels to be written from timeseries object.
        """
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s' %
                    (channel, str(TimeseriesUtility.get_channels(timeseries))))
        stats = timeseries[0].stats

        out.write(self._format_header(stats))

        out.write(self._format_data(timeseries, channels))

    def _format_header(self, stats):
        """format headers for VBF file

        Parameters
        ----------
            stats : List
                An object with the header values to be written.

        Returns
        -------
        str
            A string formatted to be a single header line in a VBF file.
        """
        buf = []

        observatory = stats.station
        year = str(stats.starttime.year)
        yearday = str(stats.starttime.julday).zfill(3)
        date = stats.starttime.strftime("%d-%b-%y")

        buf.append(observatory + '  ' + year + '  ' + yearday + '  ' +
                    date + '  Hvolt Hbin Evolt Ebin Zvolt Zbin Version 1.0\n')

        return ''.join(buf)

    def _format_data(self, timeseries, channels):
        """Format all data lines.

        Parameters
        ----------
            timeseries : obspy.core.Stream
                Stream containing traces with channel listed in channels
            channels : sequence
                List and order of channel values to output.

        Returns
        -------
        str
            A string formatted to be the data lines in a VBF file.
        """
        buf = []

        # create new stream
        timeseriesLocal = Stream()
        # Use a copy of the trace so that we don't modify the original.
        for trace in timeseries:
            traceLocal = trace.copy()
            if traceLocal.stats.channel == 'D':
                traceLocal.data = \
                    ChannelConverter.get_minutes_from_radians(traceLocal.data)

            # TODO - we should look into multiplying the trace all at once
            # like this, but this gives an error on Windows at the moment.
            # traceLocal.data = \
            #     numpy.round(numpy.multiply(traceLocal.data, 100)).astype(int)

            timeseriesLocal.append(traceLocal)

        traces = [timeseriesLocal.select(channel=c)[0] for c in channels]
        starttime = float(traces[0].stats.starttime)
        delta = traces[0].stats.delta

        for i in xrange(len(traces[0].data)):
            buf.append(self._format_values(
                datetime.utcfromtimestamp(starttime + i * delta),
                (t.data[i] for t in traces)))

        return ''.join(buf)

    def _format_values(self, time, values):
        """Format one line of data values.

        Parameters
        ----------
            time : datetime
                Timestamp for values.
            values : sequence
                List and order of channel values to output.
                If value is NaN, self.empty_value is output in its place.

        Returns
        -------
        unicode
            Formatted line containing values.
        """
        tt = time.timetuple()
        totalMinutes = int(tt.tm_hour * 3600 + tt.tm_min * 60 + tt.tm_sec)

        # Init the volt/bin vals to deads.
        vdead = 99.999999
        bdead = 999
        vblist = [vdead, bdead, vdead, bdead, vdead, bdead]

        # now "un-dead" the good vals, format volts as float, bins as int
        for idx, valx in enumerate(values):
            if ~numpy.isnan(valx):
                if idx == 0 or idx == 2 or idx == 4:
                    vblist[idx] = valx / 1000.
                else:
                    vblist[idx] = int(valx)

        return '{0:0>5d} {1: >10.6f} {2: >4d} {3: >10.6f} {4: >4d} ' \
                '{5: >10.6f} {6: >4d}\n'.format(totalMinutes, *vblist)

    # ===============================================
    # CODE BELOW IS FOR MAKING A BIN CHANGE LOG.
    # VBFFactory calls the '_change_' version of the
    # procedures rather than the "usual" procedures
    # ===============================================

    def write_change_log(self, out, timeseries, channels):
        """Write timeseries to vbf file.

        Parameters
        ----------
            out : file object
                File object to be written to. Could be stdout.
            timeseries : obspy.core.stream
                Timeseries object with data to be written.
            channels : array_like
                Channels to be written from timeseries object.
        """
        for channel in channels:
            if timeseries.select(channel=channel).count() == 0:
                raise TimeseriesFactoryException(
                    'Missing channel "%s" for output, available channels %s' %
                    (channel, str(TimeseriesUtility.get_channels(timeseries))))
        stats = timeseries[0].stats

        out.write(self._format_change_header(stats))

        self._format_change_data(timeseries, channels)

        if (len(Hbuf) + len(Ebuf) + len(Zbuf)) > 0:
            out.write(' C  Date       Time     DaySec     Bin change'
            '    Voltage change\n')
            out.write(''.join(Hbuf))
            out.write('\n')
            out.write(''.join(Ebuf))
            out.write('\n')
            out.write(''.join(Zbuf))
        else:
            out.write('*** No Bin Changes Found ***\n')

    def _format_change_header(self, stats):
        """format headers for VBF file

        Parameters
        ----------
            stats : List
                An object with the header values to be written.

        Returns
        -------
        str
            A string formatted to be a single header line in a VBF file.
        """
        buf = []

        observatory = stats.station
        sttdate = stats.starttime.strftime("%d-%b-%y")
        enddate = stats.endtime.strftime("%d-%b-%y")

        buf.append('Bin Change Report: ' + observatory + '  Start Day: ' +
                    sttdate + ' End Day: ' + enddate + '\n\n')

        return ''.join(buf)

    def _format_change_data(self, timeseries, channels):
        """Format all data lines.

        Parameters
        ----------
            timeseries : obspy.core.Stream
                Stream containing traces with channel listed in channels
            channels : sequence
                List and order of channel values to output.

        Returns
        -------
        str
            A string formatted to be the data lines in a VBF file.
        """

        # create new stream
        timeseriesLocal = Stream()
        # Use a copy of the trace so that we don't modify the original.
        for trace in timeseries:
            traceLocal = trace.copy()
            if traceLocal.stats.channel == 'D':
                traceLocal.data = \
                    ChannelConverter.get_minutes_from_radians(traceLocal.data)

            # TODO - we should look into multiplying the trace all at once
            # like this, but this gives an error on Windows at the moment.
            # traceLocal.data = \
            #     numpy.round(numpy.multiply(traceLocal.data, 100)).astype(int)

            timeseriesLocal.append(traceLocal)

        traces = [timeseriesLocal.select(channel=c)[0] for c in channels]
        starttime = float(traces[0].stats.starttime)
        delta = traces[0].stats.delta

        for i in xrange(len(traces[0].data)):
            self._format_change_values(
                datetime.utcfromtimestamp(starttime + i * delta),
                (t.data[i] for t in traces))

        return

    def _format_change_values(self, time, values):
        """Format one line of data values.

        Parameters
        ----------
            time : datetime
                Timestamp for values.
            values : sequence
                List and order of channel values to output.
                If value is NaN, self.empty_value is output in its place.

        Returns
        -------
        unicode
            Formatted line containing values.
        """

        tt = time.timetuple()
        totalMinutes = int(tt.tm_hour * 3600 + tt.tm_min * 60 + tt.tm_sec)

        timestr = '{0.tm_year:0>4d}-{0.tm_mon:0>2d}-{0.tm_mday:0>2d} ' \
                  '{0.tm_hour:0>2d}:{0.tm_min:0>2d}:{0.tm_sec:0>2d}' \
                  ' ({1:0>5d})'. \
                    format(tt, totalMinutes)

        # init volt/bin vals to dead
        vdead = 99.999999
        bdead = 999
        vblist = [vdead, bdead, vdead, bdead, vdead, bdead]

        # now "un-dead" the non-nans, format volts as float, bins as int
        for idx, valx in enumerate(values):
            if ~numpy.isnan(valx):
                if idx == 0 or idx == 2 or idx == 4:
                    vblist[idx] = valx / 1000.
                else:
                    vblist[idx] = int(valx)

        if vblist[1] != 999 and h_prev[1] != 999 and vblist[1] != h_prev[1]:
            Hbuf.append('{0: >3s} {1:>s}  '
            '{2: >4d} to {3: >4d}  {4: >10.6f} to {5: >10.6f}\n'.
            format('(H)', timestr, h_prev[1],
                    vblist[1], h_prev[0], vblist[0]))

        if vblist[3] != 999 and e_prev[1] != 999 and vblist[3] != e_prev[1]:
            Ebuf.append('{0: >3s} {1:>s}  '
            '{2: >4d} to {3: >4d}  {4: >10.6f} to {5: >10.6f}\n'.
            format('(E)', timestr, e_prev[1],
                    vblist[3], e_prev[0], vblist[2]))

        if vblist[5] != 999 and z_prev[1] != 999 and vblist[5] != z_prev[1]:
            Zbuf.append('{0: >3s} {1:>s}  '
            '{2: >4d} to {3: >4d}  {4: >10.6f} to {5: >10.6f}\n'.
            format('(Z)', timestr, z_prev[1],
                    vblist[5], z_prev[0], vblist[4]))

        h_prev[0] = vblist[0]
        h_prev[1] = vblist[1]

        e_prev[0] = vblist[2]
        e_prev[1] = vblist[3]

        z_prev[0] = vblist[4]
        z_prev[1] = vblist[5]

        return

    @classmethod
    def format(self, timeseries, channels):
        """Get an VBF formatted string.

        Calls write() with a StringIO, and returns the output.

        Parameters
        ----------
            timeseries : obspy.core.Stream
                Stream containing traces with channel listed in channels
            channels : sequence
                List and order of channel values to output.

        Returns
        -------
        unicode
          VBF formatted string.
        """
        out = StringIO()
        writer = VBFWriter()
        writer.write(out, timeseries, channels)
        return out.getvalue()
