"""Parsing methods for the IMFV283 Format."""
from __future__ import absolute_import

import math
import numpy
import sys
import obspy
from obspy.core import UTCDateTime

from . import imfv283_codes

# values that represent missing data points in IAGA2002
DEAD_VALUE = 65535

HEADER_SIZE = 37
MSG_SIZE_100B = 190
MSG_SIZE_300B = 191
BIAS = 8192
SHIFT = 1048576

# Documentation list the second channel as D, but we know that for
# USGS, it's actually E. Since only USGS and Canada (YXZF) use GOES
# we are specfying it as E.
CHANNELS = {
    0: ['X', 'Y', 'Z', 'F'],
    1: ['H', 'E', 'Z', 'F'],
    2: ['1', 'D', 'I', 'F'],
    3: ['1', '2', '3', '4']
}


class IMFV283Parser(object):
    """IMFV283 parser.

    Based on documentation at:
        http://www.intermagnet.org/data-donnee/formats/imfv283e-eng.php

    Attributes
    ----------
    headers : dict
        parsed IMFV283 headers.
    channels : array
        parsed channel names.
    data : dict
        keys are channel names (order listed in ``self.channels``).
        values are ``numpy.array`` of timeseries values, array values are
        ``numpy.nan`` when values are missing.
    Notes:
    ------
    IMFV283 is the format that data is sent over the GOES satellite.
    Data is sent in 12 minute packets.
    When an outage occurs at the observatory, generally speaking, only the most
    recent data is sent. At the reciever data is collected and kept for up to
    30 days. At this point, the utility we use to read data from the receiver
    simply gets all the packets from the last time it connected, and appends
    them to the data file.
    We can change this to get smarter, but right now, there's no need to.
    """

    def __init__(self):
        """Create a new IMFV283 parser."""
        self._parsedata = None
        self.stream = obspy.core.Stream()

    def parse(self, data):
        """Parse a string containing IMFV283 formatted data.

        Parameters
        ----------
        data : str
            IMFV283 formatted file contents.
        """
        lines = data.splitlines()
        for line in lines:
            # if line isn't at least 37 characters, there's no need to proceed.
            if len(line) <= HEADER_SIZE:
                sys.stderr.write('Bad Header length\n')
                continue

            try:
                msg_header = self._parse_msg_header(line)

                data_len = msg_header['data_len']
                # check message size indicates data exists
                if data_len < MSG_SIZE_100B or data_len > MSG_SIZE_300B:
                    sys.stderr.write('Incorrect data Length \n')
                    continue

                goes_data = self._process_ness_block(
                        line,
                        imfv283_codes.OBSERVATORIES[msg_header['obs']],
                        data_len)

                goes_header = self._parse_goes_header(goes_data)
                data = self._get_data(goes_header, goes_data)
                self._post_process(data, msg_header, goes_header)
            except (KeyError, IndexError, ValueError):
                sys.stderr.write("Incorrect data line ")
                sys.stderr.write(line)

    def _get_data(self, header, data):
        """get data from data packet

        Parameters
        ----------
        header : dict
            contains the header information for the data packet
        data : bytearray
            contains the encoded channel data
        Returns
        -------
        dict
            dictionary of channel data arrays.
        """
        parse_data = {}
        channels = CHANNELS[header['orient']]
        for channel in channels:
            parse_data[channel] = []

        bytecount = 30
        for cnt in xrange(0, 12):
            # get data in 2 byte pairs as integers.
            d1 = 0x100 * data[bytecount] + data[bytecount + 1]
            d2 = 0x100 * data[bytecount + 2] + data[bytecount + 3]
            d3 = 0x100 * data[bytecount + 4] + data[bytecount + 5]
            d4 = 0x100 * data[bytecount + 6] + data[bytecount + 7]
            bytecount += 8

            parse_data[channels[0]].append(d1)
            parse_data[channels[1]].append(d2)
            parse_data[channels[2]].append(d3)
            parse_data[channels[3]].append(d4)

        return parse_data

    def _get_data_offset(self, data_len):
        """get the data offset for the ness blocks

        Parameters
        ----------
        data_len : int
            the length of the data provided by the message header.
        Returns
        -------
        int
            offset to the data in the ness block
        Notes
        -----
        The data block has an extra flag tacked onto the start. We detect
        this by looking at the data length. Since we don't use this
        flag we skip it by adding to the data offset.
        """
        if data_len == MSG_SIZE_300B:
            return HEADER_SIZE + 1
        return HEADER_SIZE

    def _get_startime(self, msg_header, goes_header):
        """Get Starttime by combining headers.

        Parameters
        ----------
        msg_header : dict
            header information for the message packet
        goes_header : dict
            header information for the goes data packet

        Returns
        -------
        goes_time : UTCDateTime
            The starttime for the goes data packet.
        msg_time : UTCDateTime
            The starttime for the goes message packet.
        Notes
        -----
        The goes data packet stores the day of the year, and the minute of
        the day.  To get a complete starttime, we use the year for the message
        and correct for the case where the message came in a new year, vs.
        when the data packet was created.
        """
        msg_time = msg_header['transmission_time']
        msg_year = 2000 + int(msg_time[0:2])
        msg_day = int(msg_time[2:5])

        oridinal_time = '%04d%sT%s' % (msg_year, msg_time[2:5], msg_time[5:])
        msg_time = UTCDateTime(oridinal_time)

        if msg_day == 1 and goes_header['day'] >= 365:
            msg_year -= 1

        hour = math.floor(goes_header['minute'] / 60.)
        minute = goes_header['minute'] % 60

        ordinal_time = '%04d%03dT%02d%02d' % (msg_year, goes_header['day'],
                hour, minute)
        goes_time = UTCDateTime(ordinal_time)
        return (goes_time, msg_time)

    def _parse_goes_header(self, data):
        """ parse goes data header

        Parameters
        ----------
        data : bytearray
            The bytearray containing the goes data packet.
        Returns
        -------
        dict
            dictionary containing the required values for decoding the
            data packet.
        """
        header = {}

        # day of year and minute of day are combined into 3 bytes
        header['day'] = data[0] + 0x100 * (data[1] & 0xF)
        header['minute'] = (data[2] & 0xFF) * 0x10 + data[1] / 0x10

        # offset values for each channel are in bytes 3,4,5,6 respectively.
        header['offset'] = data[3:7]

        # Not used.  alert_capable = (goes_block[7] & 0x01)
        # orient code. The orientation of the instrument (HEZF, etc.)
        header['orient'] = data[7] / 0x40

        # scale values bits 0,1,2,3 of byte 7.
        # Either 1 if bit not set, 2 if bit is set.
        scale1 = 1
        scale2 = 1
        scale3 = 1
        scale4 = 1
        if (data[7] & 0x20) > 0:
            scale1 = 2
        if (data[7] & 0x10) > 0:
            scale2 = 2
        if (data[7] & 0x8) > 0:
            scale3 = 2
        if (data[7] & 0x4) > 0:
            scale4 = 2
        header['scale'] = [scale1, scale2, scale3, scale4]

        return header

    def _parse_msg_header(self, msg):
        """parse the goes message header

        Parameters
        ----------
        msg : array of chars
            The message as provided by the goes receipt software, open dcs.
        Returns
        -------
        dict
            a dictionary of the header information we use.
        """
        header = {}

        header['daps_platform'] = msg[0:8]
        header['obs'] = imfv283_codes.PLATFORMS[header['daps_platform']]
        # if it's not in the observatory dictionary, we ignore it.
        if header['obs'] is None:
            return header

        # get the time of the transmission
        header['transmission_time'] = msg[8:19]
        header['data_len'] = int(msg[32:37])
        return header

    def _post_process(self, data, msg_header, goes_header):
        """process parsed data

        Parameters
        ----------
        data: dict
            parsed data by channel
        msg_header: dict
            parsed header of the message
        goes_header: dict
            parsed header of the goes data

        """
        (goes_time, msg_time) = self._get_startime(msg_header, goes_header)
        if (msg_time - goes_time) > (24 * 60):
            sys.stderr.write('data over twice as old as the message')
            return

        scale = goes_header['scale']
        offset = goes_header['offset']
        orientation = goes_header['orient']
        for channel, loc in zip(CHANNELS[orientation], xrange(0, 4)):
            stats = obspy.core.Stats()
            stats.channel = channel
            stats.sampling_rate = 0.0166666666667
            stats.starttime = goes_time
            stats.npts = 12
            stats.station = msg_header['obs']

            numpy_data = numpy.array(data[channel], dtype=numpy.float64)
            numpy_data[numpy_data == DEAD_VALUE] = numpy.nan
            # Data values need to be scaled, offset and shifted into the
            # correct 10th nanotesla value.
            # For our convenience we convert to nanotesla values.
            numpy_data = numpy.multiply(numpy_data, scale[loc])
            numpy_data = numpy.add(numpy_data, offset[loc] * BIAS - SHIFT)
            numpy_data = numpy.divide(numpy_data, 10.0)

            trace = obspy.core.Trace(numpy_data, stats)
            self.stream += trace

    def _process_ness_block(self, msg, domsat, data_len):
        """process the "ness" block of data into an IMFV283 data block.

        Parameters
        ----------
        msg : array
            unsigned chars
        domsat : dict
            Dictionary of observatory dependent information used to decode
            ness block.
        data_len : int
            data_len provided by the message header.
        """
        goes_block = bytearray(126)
        ness_byte = 0
        goes_byte = 0

        if data_len == MSG_SIZE_300B:
            offset = HEADER_SIZE + 1
        else:
            offset = HEADER_SIZE

        for cnt in xrange(0, 63):
            # Convert 3 byte "pair" into ordinal values for manipulation.
            byte3 = ord(msg[offset + ness_byte + 2])
            byte2 = ord(msg[offset + ness_byte + 1])
            byte1 = ord(msg[offset + ness_byte])

            goes_value1 = (byte3 & 0x3F) + ((byte2 & 0x3) * 0x40)
            goes_value2 = ((byte2 / 0x4) & 0xF) + ((byte1 & 0xF) * 0x10)

            # swap the bytes depending on domsat information.
            if domsat['swap_hdr'] and cnt <= 11 or \
                    domsat['swap_data'] and cnt > 11:
                goes_block[goes_byte] = goes_value2
                goes_block[goes_byte + 1] = goes_value1
            else:
                goes_block[goes_byte] = goes_value1
                goes_block[goes_byte + 1] = goes_value2

            ness_byte += 3
            goes_byte += 2

        return goes_block
