# -*- coding: utf-8 -*-
"""
Input Client for Edge/CWB/QueryMom.

:copyright:
    USGS
:license:
    GNU General Public License (GPLv2)
    (http://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
"""
# ensure geomag is on the path before importing
try:
    import geomagio  # noqa (tells linter to ignor this line.)
except:
    from os import path
    import sys
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, '../..')))

from obspy.core.utcdatetime import UTCDateTime
from datetime import datetime
from geomagio import TimeseriesFactoryException
import struct
import socket  # noqa
from time import sleep

MAXINPUTSIZE = 32767


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

    def __init__(self, tag='', host='', port=0, cwbhost='', cwbport=0):
        self.tag = tag
        self.host = host
        self.port = port
        self.cwbhost = cwbhost or ''
        self.cwbport = cwbport
        self.socket = None
        self.cwbsocket = None
        self.buf = None
        self.seq = 0
        self.tagseq = 0
        self.now = UTCDateTime(datetime.utcnow())
        self.dummy = UTCDateTime(datetime.utcnow())
        self.timeout = 10
        self.seedname = ''

        if len(self.tag) > 10:
            raise TimeseriesFactoryException(
                'Tag limited to 10 characters')

    def close(self):
        """close the open sockets
        """
        # make certain sockets have time to clear
        sleep(1)
        if self.socket is not None:
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
            self.socket = None
        if self.cwbsocket is not None:
            self.socket.shutdown(socket.SHUT_WR)
            self.cwbsocket.close()
            self.cwbsocket = None

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
        self.send(seedname, -2, [], self.dummy, 0., 0, 0, 0, 0)

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

    def send(self, seedname, nsamp, samples, time, rate,
            activity=0, ioclock=0, quality=0, timingquality=0):
        """ Send a block of data to the Edge/CWB combination.

        PARAMETERS
        ----------
          seedname: The 12 character seedname of the channel
              NNSSSSSCCCLL fixed format
          nsamp The number of data samples (negative will force buffer clear)
          samples: An int array with the samples
          time: With the time of the first sample as a UTCDateTime
          rate: The data rate in Hertz
          activity: The activity flags per the SEED manual
          ioClock: The IO/CLOCK flags per the SEED manual
          quality: The data Quality flags per the SEED manual
          timingQuality: The overall timing quality (must be 0-100)

        Raises
        ------
        UnknownHostException - if the socket will not open

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
        if nsamp > 32767:
            raise TimeseriesFactoryException(
                'Edge input limited to 32767 integers per packet.')

        # If this is a new channel, reset sequence.
        if self.seedname != seedname:
            self.seedname = seedname
            self.seq = 0

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
        if nsamp > 0:
            packStr = '%s%d%s' % (packStr, nsamp, 'i')
            buf = struct.pack(packStr, 0xa1b2, nsamp, seedname, yr, doy,
                          ratemantissa, ratedivisor, activity, ioclock,
                          quality, timingquality, secs, usecs, self.seq,
                          *samples)
        else:
            buf = struct.pack(packStr, 0xa1b2, nsamp, seedname, yr, doy,
                          ratemantissa, ratedivisor, activity, ioclock,
                          quality, timingquality, secs, usecs, self.seq)
        self.seq += 1

        # Try and send the packet, if the socket doesn't exist open it.
        try:
            # Older then 10 days, send to cwb.
            if (abs(self.now.timestamp - time.timestamp) > 864000 and
                    self.cwbport > 0):
                if self.cwbsocket is None:
                    self.cwbsocket = self._open_socket()
                    self.cwbsocket.sendall(self._get_next_tag())
                self.cwbsocket.sendall(buf)
            # Realtime data send to edge.
            else:
                if self.socket is None:
                    self.socket = self._open_socket()
                    self.socket.sendall(self._get_next_tag())
                self.socket.sendall(buf)
        except socket.error, v:
            sys.stderr.write('sockect error %d' % v[0])

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
        while not done:
            try:
                newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                newsocket.connect((self.host, self.port))
                done = True
            except socket.error, v:
                sys.stderr.write('Could not connect to socket, trying again')
                sys.stderr.write('sockect error %d' % v[0])
                sleep(1)
        return newsocket

    def _get_next_tag(self):
        """Get the next tag name

        RETURNS
        -------
        str

        NOTES
        -----
        The tag packet is used to by the edge server to log/determine a new
        "user" has connected to the edge, not one who's connection dropped,
        and is trying to continue sending data.
        This routine adds a number to the tag provided by the user. It's
        probably unneeded.
        """
        tmp = []
        tmp.append(self.tag)
        tmp.append(str(self.tagseq))
        tmp.append('            ')
        tg = ''.join(tmp)
        zeros = [0] * 6
        tb = struct.pack('!H1h12s6i', 0xa1b2, -1, tg, *zeros)
        if self.tagseq > 99:
            self.tagseq = 0
        self.tagseq += 1
        return tb
