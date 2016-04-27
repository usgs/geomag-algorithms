"""Parsing methods for the temp/volt Format."""


import numpy

# values that represent missing data points in TEMP
NINES = numpy.int('9999999')
NINES_RAW = numpy.int('99999990')
NINES_DEG = numpy.int('9999')


class TEMPParser(object):
    """TEMP parser.

    Attributes
    ----------
    header : dict
        parsed TEMP header.
    channels : array
        parsed channel names.
    times : array
        parsed timeseries times.
    data : dict
        keys are channel names (order listed in ``self.channels``).
        values are ``numpy.array`` of timeseries values, array values are
        ``numpy.nan`` when values are missing.
    """

    def __init__(self):
        """Create a new TEMP parser."""
        # header fields
        self.header = {}
        # array of channel names
        self.channels = []
        # timestamps of data (datetime.datetime)
        self.times = []
        # dictionary of data (channel : numpy.array<float64>)
        self.data = {}
        # temporary storage for data being parsed
        self._parsedata = None

    def parse(self, data):
        """Parse a string containing TEMP formatted data.

        Parameters
        ----------
        data : str
            temp/volt formatted file contents.
        """
        self._set_channels()

        parsing_header = True
        lines = data.splitlines()
        for line in lines:
            if parsing_header:
                self._parse_header(line)
                parsing_header = False
            else:
                self._parse_data(line)
        self._post_process()

    def _parse_header(self, line):
        """Parse header line.

        Adds value to ``self.header``.
        """
        self.header['header'] = line
        self.header['station'] = line[0:3]
        self.header['year'] = line[5:9]
        self.header['yearday'] = line[11:14]
        self.header['date'] = line[16:25]

        return

    def _parse_data(self, line):
        """Parse one data point in the timeseries.

        Adds time to ``self.times``.
        Adds channel values to ``self.data``.
        """
        t, d1, d2, d3, d4 = self._parsedata

        t.append(line[0:4])
        d1.append(int(line[5:13]))
        d2.append(int(line[14:22]))
        d3.append(int(line[23:31]))
        d4.append(int(line[32:40]))

    def _post_process(self):
        """Post processing after data is parsed.

        Converts data to numpy arrays.
        Replaces empty values with ``numpy.nan``.
        """
        self.times = self._parsedata[0]

        for channel, data in zip(self.channels, self._parsedata[1:]):
            data = numpy.array(data, dtype=numpy.float64)
            # filter empty values
            data[data == NINES] = numpy.nan
            data = numpy.divide(data, 100)
            self.data[channel] = data

        self._parsedata = None

    def _set_channels(self):
        """Adds channel names to ``self.channels``.
        Creates empty values arrays in ``self.data``.
        """
        self.channels.append('H')
        self.channels.append('E')
        self.channels.append('Z')
        self.channels.append('F')

        self._parsedata = ([], [], [], [], [])
