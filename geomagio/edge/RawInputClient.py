# -*- coding: utf-8 -*-
"""
Input Client for Edge/CWB/QueryMom.

:copyright:
    USGS
:license:
    GNU General Public License (GPLv2)
    (http://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
"""

from obspy.core.utcdatetime import UTCDateTime
from datetime import datetime
from geomagio import TimeseriesFactoryException
import struct
import socket  # noqa
import sys
from time import sleep

"""
MAXINPUTSIZE: Edge uses a short for the data count, so the max input size
    for a single data packet to edge is 32767
HOURSECONDS: The number of seconds in an hour. Used as an arbitrary size
    for sending seconds data.
DAYMINUTES: The numbers of minutes in a day. Used as the size for sending
    minute data,  since Edge stores by the day.
"""
MAXINPUTSIZE = 32767
HOURSECONDS = 3600
DAYMINUTES = 1440

TAG = -1
FORCEOUT = -2


class RawInputClient():
    Sequence = 0
    Seedname = ''
    """RawInputClient for direct to edge data.
    Parameters
    ----------
    tag: str
        A string used by edge to make certain a socket hasn't been
        opened by a different user, and to log transactions.
    host: str
        The IP address of the target host RawInputServer
    port: int
        The port on the IP of the RawInputServer
    cwbhost: str
        The host to use for data out of the 10 day window
    cwbport: int
        The port to use for data out of the 10 day window

        Note: cwbhost/cwbport are not currently used for geomag data

    Raises
    ------
    TimeseriesFactoryException

    NOTES
    -----
    Uses sockets to send data to an edge. See send method for packet encoding
    """

    def __init__(self, tag='', host='', port=0):
        self.tag = tag
        self.host = host
        self.port = port
        self.socket = None
        self.buf = None
        self.seedname = ''

        if len(self.tag) > 10:
            raise TimeseriesFactoryException(
                'Tag limited to 10 characters')

    def close(self):
        """close the open sockets
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def forceout(self, seedname):
        """ force edge to recognize data

        PARAMETERS
        ----------
        seedname: str
            The seedname of the data
        NOTES
        -----
        When sending data to edge it hangs on to the data, until either
            enough data has accumulated, or enough time has passed. At that
            point, it makes the new data available for reading.
            Fourceout tells edge that we're done sending data for now, and
            to go ahead and make it available
        """
        self.send(seedname, [], UTCDateTime(datetime.utcnow()),
                0., 0, 0, 0, 0, True)

    def create_seedname(self, observatory, channel, location='R0',
                network='NT'):
        """create a seedname for communication with edge.

        PARAMETERS
        ----------
        observatory: str
            observatory code.
        channel: str
            channel to be written
        location: str
            location code
        network: str
            network code

        RETURNS
        -------
        str
            the seedname

        NOTES
        -----
        The seedname is in the form NNSSSSSCCCLL if a parameter is not
        of the correct length,  it should be padded with spaces to be of
        the correct length.  We only expect observatory to ever be of an
        incorrect length.
        """
        return network + observatory.ljust(5) + channel + location

    def send_trace(self, seedname, interval, trace):
        """send an obspy trace using send.

        PARAMETERS
        ----------
        seedname: str
            the seedname for the trace
        interval: {'daily', 'hourly', 'minute', 'second'}
            data interval.
        trace: obspy.core.trace

        NOTES
        -----
        Edge only takes a short as the max number of samples it takes at one
        time. For ease of calculation, we break a trace into managable chunks
        according to interval type.
        """
        totalsamps = len(trace.data)
        starttime = trace.stats.starttime

        if interval == 'second':
            nsamp = HOURSECONDS
            timeoffset = 1
            samplerate = 1.
        elif interval == 'minute':
            nsamp = DAYMINUTES
            timeoffset = 60
            samplerate = 1. / 60
        elif interval == 'hourly':
            nsamp = MAXINPUTSIZE
            timeoffset = 3600
            samplerate = 1. / 3600
        elif interval == 'daily':
            nsamp = MAXINPUTSIZE
            timeoffset = 86400
            samplerate = 1. / 86400
        else:
            raise TimeseriesFactoryException(
                    'Unsupported interval for RawInputClient')

        for i in xrange(0, totalsamps, nsamp):
            if totalsamps - i < nsamp:
                endsample = totalsamps
            else:
                endsample = i + nsamp
            nsamp = endsample - i
            endtime = starttime + (nsamp - 1) * timeoffset
            trace_send = trace.slice(starttime, endtime)
            self.send(seedname, trace_send.data, starttime,
                    samplerate, 0, 0, 0, 0)
            starttime += nsamp * timeoffset

    def send(self, seedname, samples, time, rate,
            activity=0, ioclock=0, quality=0, timingquality=0,
            forceout=False):
        """ Send a block of data to the Edge/CWB combination.

        PARAMETERS
        ----------
        seedname: str
            The 12 character seedname of the channel NNSSSSSCCCLL fixed format
        samples: array like
            An int array with the samples
        time: UTCDateTime
            time of the first sample
        rate: int
            The data rate in Hertz
        activity: int
            The activity flags per the SEED manual
        ioClock: int
            The IO/CLOCK flags per the SEED manual
        quality: int
            The data Quality flags per the SEED manual
        timingQuality: int [0-100]
            The overall timing quality
        forceout: boolean
            indicates the packet to be sent will have a nsamp value of -1,
            to tell edge to force the data to be written

        Raises
        ------
        TimeseriesFactoryException - if the socket will not open

        NOTES
        -----
        Data is encoded into a C style structure using struct.pack with the
        following variables and type.
            0xa1b2 (short)
            nsamp (short)
            seedname (12 char)
            yr (short)
            doy (short)
            ratemantissa (short)
            ratedivisor (short)
            activity (byte)
            ioClock (byte)
            quality (byte)
            timeingQuality (byte)
            secs (int)
            seq  (int)   Seems to be the miniseed sequence, but not certain.
                        basically we increment it for every new set we send
            data [int]

        Notice that we expect the data to already be ints.
        The nsamp parameter is signed. If it's positive we send a data packet.
            -1 is for a tag packet (see _get_next_tag method)
            -2 is for a force out packet (see forceout method)
        """
        nsamp = len(samples)
        if nsamp > 32767:
            raise TimeseriesFactoryException(
                'Edge input limited to 32767 integers per packet.')

        # If this is a new channel, reset sequence.
        if RawInputClient.Seedname != seedname:
            RawInputClient.Seedname = seedname
            RawInputClient.Sequence = 0

        # Get time parameters for packet
        yr = time.year
        doy = time.datetime.timetuple().tm_yday
        secs = time.hour * 3600 + time.minute * 60 + time.second
        usecs = time.microsecond

        # Calculate ratemantissa and ratedivisor for edge.
        # force one minute data to be -60 and 1
        if rate > 0.9999:
            ratemantissa = int(rate * 100 + 0.001)
            ratedivisor = -100
        elif rate * 60. - 1.0 < 0.00000001:          # one minute data
            ratemantissa = -60
            ratedivisor = 1
        else:
            ratemantissa = int(rate * 10000. + 0.001)
            ratedivisor = -10000

        # Construct the packet to be sent.
        packStr = '!1H1h12s4h4B3i'
        if forceout:
            buf = struct.pack(packStr, 0xa1b2, FORCEOUT, seedname, yr,
                    doy, ratemantissa, ratedivisor, activity, ioclock,
                    quality, timingquality, secs, usecs,
                    RawInputClient.Sequence)
        else:
            packStr = '%s%d%s' % (packStr, nsamp, 'i')
            buf = struct.pack(packStr, 0xa1b2, nsamp, seedname, yr, doy,
                    ratemantissa, ratedivisor, activity, ioclock, quality,
                    timingquality, secs, usecs, RawInputClient.Sequence,
                    *samples)

        RawInputClient.Sequence +=1

        # Try and send the packet, if the socket doesn't exist open it.
        try:
            if self.socket is None:
                self.socket = self._open_socket()
                self.socket.sendall(self._get_tag())
            self.socket.sendall(buf)
        except socket.error, v:
            error = 'Socket error %d' % v[0]
            sys.stderr.write(error)
            raise TimeseriesFactoryException(error)

    def _open_socket(self):
        """Open a socket

        RETURNS
        -------
        socket

        NOTES
        -----
        Loops until a socket is opened, with a 1 second wait between attempts
        """
        done = False
        newsocket = None
        trys = 0
        while not done:
            try:
                newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                newsocket.connect((self.host, self.port))
                done = True
            except socket.error, v:
                sys.stderr.write('Could not connect to socket, trying again')
                sys.stderr.write('sockect error %d' % v[0])
                sleep(1)
            if trys > 2:
                raise TimeseriesFactoryException('Could not open socket')
            trys += 1
        return newsocket

    def _get_tag(self):
        """Get tag struct

        RETURNS
        -------
        str

        NOTES
        -----
        The tag packet is used to by the edge server to log/determine a new
        "user" has connected to the edge, not one who's connection dropped,
        and is trying to continue sending data.
        The packet uses -1 in the nsamp position to indicate it's a tag packet
        The tag is right padded with spaces.
        The Packet is right padded with zeros
        The Packet must be 40 Bytes long.
        """
        tg = self.tag + '            '
        tb = struct.pack('!1H1h12s6i', 0xa1b2, TAG, tg[:12],
                0, 0, 0, 0, 0, 0)
        return tb
