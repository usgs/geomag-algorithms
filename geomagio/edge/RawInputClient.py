from __future__ import unicode_literals
from builtins import range, str

import socket  # noqa
import struct
import sys
from datetime import datetime
from ..TimeseriesFactoryException import TimeseriesFactoryException
from obspy.core import UTCDateTime
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

"""
PACKSTR, TAGSTR: String's used by pack.struct, to indicate the data format
    for that packet.
PACKEHEAD: The code that leads a packet being sent to Edge.
"""
PACKSTR = '!1H1h12s4h4B3i'
TAGSTR = '!1H1h12s6i'
PACKETHEAD = 0xa1b2

"""
TAG, FORCEOUT: Flags that indicate to edge that a "data" packet has a specific
    function. Goes in the nsamp position of the packet header.
"""
TAG = -1
FORCEOUT = -2


class RawInputClient():

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
    station: str
        station code.
    channel: str
        channel to be written
    location: str
        location code
    network: str
        network code
    activity: int
        The activity flags per the SEED manual
    ioClock: int
        The IO/CLOCK flags per the SEED manual
    quality: int
        The data Quality flags per the SEED manual
    timingQuality: int [0-100]
        The overall timing quality

    Raises
    ------
    TimeseriesFactoryException

    NOTES
    -----
    Uses sockets to send data to an edge. See send method for packet encoding
    """

    def __init__(self, tag='', host='', port=0, station='', channel='',
            location='', network='', activity=0, ioclock=0, quality=0,
            timingquality=0):
        self.tag = tag
        self.host = host
        self.port = port
        self.activity = activity
        self.ioclock = ioclock
        self.quality = quality
        self.timingquality = timingquality

        self.socket = None
        self.buf = None
        self.sequence = 0

        self.seedname = self.create_seedname(station, channel,
                location, network)

        if len(self.tag) > 10:
            raise TimeseriesFactoryException(
                'Tag limited to 10 characters')

    def close(self):
        """close the open sockets
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None

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
        return str(network +
                observatory.ljust(5) +
                channel +
                location).encode()

    def forceout(self):
        """ force edge to recognize data
        NOTES
        -----
        When sending data to edge it hangs on to the data, until either
            enough data has accumulated, or enough time has passed. At that
            point, it makes the new data available for reading.
            Fourceout tells edge that we're done sending data for now, and
            to go ahead and make it available
        """
        buf = self._get_forceout(UTCDateTime(datetime.utcnow()), 0.)
        self._send(buf)

    def send_trace(self, interval, trace):
        """send an obspy trace using send.

        PARAMETERS
        ----------
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

        for i in range(0, totalsamps, nsamp):
            if totalsamps - i < nsamp:
                endsample = totalsamps
            else:
                endsample = i + nsamp
            nsamp = endsample - i
            endtime = starttime + (nsamp - 1) * timeoffset
            trace_send = trace.slice(starttime, endtime)
            buf = self._get_data(trace_send.data, starttime, samplerate)
            self._send(buf)
            starttime += nsamp * timeoffset

    def _send(self, buf):
        """ Send a block of data to the Edge/CWB combination.

        PARAMETERS
        ----------
        samples: array like
            An int array with the samples
        time: UTCDateTime
            time of the first sample
        rate: int
            The data rate in Hertz
        forceout: boolean
            indicates the packet to be sent will have a nsamp value of -2,
            to tell edge to force the data to be written

        Raises
        ------
        TimeseriesFactoryException - if the socket will not open
        """

        # Try and send the packet, if the socket doesn't exist open it.
        try:
            if self.socket is None:
                self._open_socket()
            self.socket.sendall(buf)
            self.sequence += 1
        except socket.error as v:
            error = 'Socket error %d' % v[0]
            sys.stderr.write(error)
            raise TimeseriesFactoryException(error)

    def _get_forceout(self, time, rate):
        """
        PARAMETERS
        ----------
        time: UTCDateTime
            time of the first sample
        rate: int
            The data rate in Hertz

        RETURNS
        -------
        str

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
                        basically we increment it for every new packet we send

        The nsamp parameter is signed.
            -2 is for a force out packet

        """
        yr, doy, secs, usecs = self._get_time_values(time)
        ratemantissa, ratedivisor = self._get_mantissa_divisor(rate)

        buf = struct.pack(PACKSTR, PACKETHEAD, FORCEOUT, self.seedname, yr,
                doy, ratemantissa, ratedivisor, self.activity, self.ioclock,
                self.quality, self.timingquality, secs, usecs,
                self.sequence)
        return buf

    def _get_data(self, samples, time, rate):
        """
        PARAMETERS
        ----------
        samples: array like
            An int array with the samples
        time: UTCDateTime
            time of the first sample
        rate: int
            The data rate in Hertz

        RETURNS
        -------
        str

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

        """
        nsamp = len(samples)
        if nsamp > 32767:
            raise TimeseriesFactoryException(
                'Edge input limited to 32767 integers per packet.')

        yr, doy, secs, usecs = self._get_time_values(time)
        ratemantissa, ratedivisor = self._get_mantissa_divisor(rate)

        packStr = '%s%d%s' % (PACKSTR, nsamp, 'i')
        bpackStr = str(packStr).encode()
        buf = struct.pack(bpackStr, PACKETHEAD, nsamp, self.seedname, yr, doy,
                ratemantissa, ratedivisor, self.activity, self.ioclock,
                self.quality, self.timingquality, secs, usecs, self.sequence,
                *samples)

        return buf

    def _get_mantissa_divisor(self, rate):
        """
        PARAMETERS
        ----------
        rate: int
            The data rate in Hertz

        RETURNS
        -------
        tuple: (ratemantissa, ratedivosor)
            ratemantissa: int
            ratedivosor: int
        """
        if rate > 0.9999:
            ratemantissa = int(rate * 100 + 0.001)
            ratedivisor = -100
        elif rate * 60. - 1.0 < 0.00000001:          # one minute data
            ratemantissa = -60
            ratedivisor = 1
        else:
            ratemantissa = int(rate * 10000. + 0.001)
            ratedivisor = -10000

        return (ratemantissa, ratedivisor)

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
        tg = str(self.tag + '            ').encode()
        tb = struct.pack(TAGSTR, PACKETHEAD, TAG, tg[:12],
                0, 0, 0, 0, 0, 0)
        return tb

    def _get_time_values(self, time):
        """
        PARAMETERS
        ----------
        time: UTCDateTime
            time of the first sample

        RETURNS
        -------
        tuple: (yr, doy, secs, usecs)
            yr: int
            doy: int
            secs: int
            usecs: int
        """
        yr = time.year
        doy = time.datetime.timetuple().tm_yday
        secs = time.hour * 3600 + time.minute * 60 + time.second
        usecs = time.microsecond

        return (yr, doy, secs, usecs)

    def _open_socket(self):
        """Open a socket

        NOTES
        -----
        Loops until a socket is opened, with a 1 second wait between attempts
        Sends tag.
        """
        done = False
        newsocket = None
        trys = 0
        while not done:
            try:
                newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                newsocket.connect((self.host, self.port))
                done = True
            except socket.error as v:
                sys.stderr.write('Could not connect to socket, trying again')
                sys.stderr.write('sockect error %d' % v[0])
                sleep(1)
            if trys > 2:
                raise TimeseriesFactoryException('Could not open socket')
            trys += 1
        self.socket = newsocket
        self.socket.sendall(self._get_tag())
