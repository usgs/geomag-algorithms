"""Parsing methods for the IMFV122 Format."""


import numpy
from obspy.core import UTCDateTime

# values that represent missing data points in IAGA2002
EIGHTS = numpy.float64("888888")
NINES = numpy.float64("999999")


class IMFV122Parser(object):
    """IMFV122 parser.

    Based on documentation at:
      http://www.intermagnet.org/data-donnee/formats/imfv122-eng.php

    Attributes
    ----------
    metadata : dict
        parsed IMFV122 metadata.
    channels : array
        parsed channel names.
    times : array
        parsed timeseries times.
    data : dict
        keys are channel names (order listed in ``self.channels``).
        values are ``numpy.array`` of timeseries values, array values are
        ``numpy.nan`` when values are missing.
    """

    def __init__(self, observatory=None):
        """Create a new IAGA2002 parser."""
        # header fields
        self.metadata = {"network": "NT", "station": observatory}
        # array of channel names
        self.channels = []
        # timestamps of data (datetime.datetime)
        self.times = []
        # dictionary of data (channel : numpy.array<float64>)
        self.data = {}
        # temporary storage for data being parsed
        self._parsedata = ([], [], [], [], [])

    def parse(self, data):
        """Parse a string containing IAGA2002 formatted data.

        Parameters
        ----------
        data : str
            IAGA 2002 formatted file contents.
        """
        station = data[0:3]
        lines = data.splitlines()
        for line in lines:
            if line.startswith(station):
                self._parse_header(line)
            else:
                self._parse_data(line)
        self._post_process()

    def _parse_header(self, line):
        """Parse header line.

        Adds value to ``self.headers``.
        """
        (
            observatory,
            date,
            doy,
            start,
            components,
            type,
            gin,
            colalong,
            decbas,
            reserved,
        ) = line.split()

        self.channels = list(components)
        self.metadata["declination_base"] = int(decbas)
        self.metadata["geodetic_latitude"] = float(colalong[:4]) / 10
        self.metadata["geodetic_longitude"] = float(colalong[4:]) / 10
        self.metadata["station"] = observatory
        self.metadata["gin"] = gin

        year = 1900 + int(date[-2:])
        julday = int(doy)
        hour = 0
        minute = 0
        if year < 1971:
            year = year + 100
        if len(start) == 2:
            # minutes data
            hour = int(start)
            self._delta = 60
        else:
            # seconds data
            dayminute = int(start)
            hour = int(dayminute / 60)
            minute = dayminute % 60
            self._delta = 60
        self._nexttime = UTCDateTime(year=year, julday=julday, hour=hour, minute=minute)

    def _parse_data(self, line):
        """Parse one data point in the timeseries.

        Adds time to ``self.times``.
        Adds channel values to ``self.data``.
        """
        (d11, d21, d31, d41, d12, d22, d32, d42) = line.split()
        t, d1, d2, d3, d4 = self._parsedata
        t.append(self._nexttime)
        d1.append(d11)
        d2.append(d21)
        d3.append(d31)
        d4.append(d41)
        self._nexttime = self._nexttime + self._delta
        t.append(self._nexttime)
        d1.append(d12)
        d2.append(d22)
        d3.append(d32)
        d4.append(d42)
        self._nexttime = self._nexttime + self._delta

    def _post_process(self):
        """Post processing after data is parsed.

        Converts data to numpy arrays.
        Replaces empty values with ``numpy.nan``.
        """
        self.times = self._parsedata[0]
        for channel, data in zip(self.channels, self._parsedata[1:]):
            data = numpy.array(data, dtype=numpy.float64)
            data[data == EIGHTS] = numpy.nan
            data[data == NINES] = numpy.nan
            if channel == "D":
                data = data / 100
            else:
                data = data / 10
            self.data[channel] = data
        self._parsedata = None
