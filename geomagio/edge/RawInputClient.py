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
import numpy.ma as ma
import numpy
import struct
import socket  # noqa
"""
  TODO: This version doesn't keep the socket open. A version
    is needed that keeps the socket open for further sends.
"""

MAXINPUTSIZE = 32767


class RawInputClient():
    """
    """

    def __init__(self, tag='', host='', port=0,
                 cwbhost=None, cwbport=0):
        """
        tag The logging tag for this client
        host THe ip address of the target host RawInputServer
        port The port on the ip of the RawInputServer
        cwbhost The host to use for data out of the 10 day window
        cwbport The port to use for data out of the 10 day window
            cwbhost/cwbport are not currently used for geomag data
        """
        self.tag = tag
        self.host = host
        self.port = port
        # self.cwbhost = host if not cwbhost else cwbhost
        # self.cwbport = port if not cwbport else port
        self.cwbhost = cwbhost
        self.cwbport = cwbport
        self.socket = None
        self.cwbsocket = None
        self.buf = None
        self.b = None
        self.seq = 1
        self.now = UTCDateTime(datetime.utcnow())
        self.dummy = UTCDateTime(datetime.utcnow())
        self.timeout = 10

        tmp = []
        tmp.append(self.tag)
        tmp.append('            ')
        tg = ''.join(tmp)
        zeros = [0] * 6
        self.tb = struct.pack('!H1h12s6i', 0xa1b2, -1, tg, *zeros)

    def close(self):
        if self.socket is not None:
            self.socket.close()
        if self.cwbsocket is not None:
            self.cwbsocket.close()

    def forceout(self, seedname):
        self.send(seedname, -2, [], self.dummy, 0., 0, 0, 0, 0)

    def create_seedname(self, obs, channel, location='R0', network='NT'):
        return network + obs.ljust(5) + channel + location

    def send(self, seedname, nsamp, samples, time, rate,
            activity, ioclock, quality, timingquality):
        """
        Send a block of data to the Edge/CWB combination.

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
        throws UnknownHostException - if the socket will not open
        """
        # 0xa1b2 (short)
        # nsamp (short)
        # seedname (12 char)
        # yr (short)
        # doy (short)
        # ratemantissa (short)
        # ratedivisor (short)
        # activity (byte)
        # ioClock (byte)
        # quality (byte)
        # timeingQuality (byte)
        # secs (int)
        # seq  (int)   Seems to be the miniseed sequence, but not certain.
        #             basically we increment it for every new set we send
        # data [int]
        if nsamp > 32767:
            raise TimeseriesFactoryException(
                'Edge input limited to 32767 integers per packet.')
        packStr = '!1H1h12s4h4B3i'

        # negative number needs to be passed to edge for processing,
        # but we need zero for the data portion of the packstring.
        if nsamp >= 0:
            nsamples = nsamp
        else:
            nsamples = 0
        packStr = '%s%d%s' % (packStr, nsamples, 'i')

        yr = time.year
        doy = time.datetime.timetuple().tm_yday

        if rate > 0.9999:
            ratemantissa = int(rate * 100 + 0.001)
            ratedivisor = -100
        elif rate * 60. - 1.0 < 0.00000001:          # one minute data
            ratemantissa = -60
            ratedivisor = 1
        else:
            ratemantissa = int(rate * 10000. + 0.001)
            ratedivisor = -10000

        seq = 0
        secs = time.hour * 3600 + time.minute * 60 + time.second
        usecs = time.microsecond

        buf = struct.pack(packStr, 0xa1b2, nsamp, seedname, yr, doy,
                          ratemantissa, ratedivisor, activity, ioclock,
                          quality, timingquality, secs, usecs, seq, *samples)
        seq += 1

        try:
            if abs(self.now.timestamp - time.timestamp) > 864000 \
                    and self.cwbport > 0:
                if self.cwbsocket is None:
                    self.cwbsocket = socket.socket(socket.AF_INET,
                            socket.SOCK_STREAM)
                    self.cwbsocket.connect((self.cwbhost, self.cwbport))
                    self.cwbsocket.sendall(self.tb)
                self.cwbsocket.sendall(buf)
            else:
                if self.socket is None:
                    self.socket = socket.socket(socket.AF_INET,
                            socket.SOCK_STREAM)
                    self.socket.connect((self.host, self.port))
                    self.socket.sendall(self.tb)
                self.socket.sendall(buf)
        except socket.error, v:
            print 'sockect error %d' % v[0]
