"""Parsing methods for the IAGA2002 Format."""


import numpy
from datetime import datetime

# values that represent missing data points in IAGA2002
EIGHTS = numpy.float64('88888.88')
NINES = numpy.float64('99999.99')


class IAGA2002Parser(object):
    """IAGA2002 parser.

    Based on documentation at:
      http://www.ngdc.noaa.gov/IAGA/vdat/iagaformat.html

    Attributes
    ----------
    headers : dict
        parsed IAGA headers.
    comments : array
        parsed comments.
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
        """Create a new IAGA2002 parser."""
        # header fields
        self.headers = {}
        # header comments
        self.comments = []
        # array of channel names
        self.channels = []
        # timestamps of data (datetime.datetime)
        self.times = []
        # dictionary of data (channel : numpy.array<float64>)
        self.data = {}
        # temporary storage for data being parsed
        self._parsedata = None

    def parse(self, data):
        """Parse a string containing IAGA2002 formatted data.

        Parameters
        ----------
        data : str
            IAGA 2002 formatted file contents.
        """
        parsing_headers = True
        lines = data.splitlines()
        for line in lines:
            if parsing_headers:
                if line.startswith(' ') and line.endswith('|'):
                    # still in headers
                    if line.startswith(' #'):
                        self._parse_comment(line)
                    else:
                        self._parse_header(line)
                else:
                    parsing_headers = False
                    self._parse_channels(line)
            else:
                self._parse_data(line)
        self._post_process()

    def _parse_header(self, line):
        """Parse header line.

        Adds value to ``self.headers``.
        """
        key = line[1:24].strip()
        value = line[24:69].strip()
        self.headers[key] = value

    def _parse_comment(self, line):
        """Parse comment line.

        Adds line to ``self.comments``.
        """
        self.comments.append(line[2:69].strip())

    def _parse_channels(self, line):
        """Parse data header that contains channel names.

        Adds channel names to ``self.channels``.
        Creates empty values arrays in ``self.data``.
        """
        iaga_code = self.headers['IAGA CODE']
        self.channels.append(line[30:40].strip().replace(iaga_code, ''))
        self.channels.append(line[40:50].strip().replace(iaga_code, ''))
        self.channels.append(line[50:60].strip().replace(iaga_code, ''))
        self.channels.append(line[60:69].strip().replace(iaga_code, ''))
        # create parsing data arrays
        self._parsedata = ([], [], [], [], [])

    def _parse_data(self, line):
        """Parse one data point in the timeseries.

        Adds time to ``self.times``.
        Adds channel values to ``self.data``.
        """
        # parsing time components is much faster
        time = datetime(
                # date
                int(line[0:4]), int(line[5:7]), int(line[8:10]),
                # time
                int(line[11:13]), int(line[14:16]), int(line[17:19]),
                # microseconds
                int(line[20:23]) * 1000)
        t, d1, d2, d3, d4 = self._parsedata
        t.append(time)
        d1.append(line[31:40])
        d2.append(line[41:50])
        d3.append(line[51:60])
        d4.append(line[61:70])

    def _post_process(self):
        """Post processing after data is parsed.

        Merges comment lines.
        Parses additional comment-based header values.
        Converts data to numpy arrays.
        Replaces empty values with ``numpy.nan``.
        """
        self.comments = self._merge_comments(self.comments)
        self.parse_comments()
        self.times = self._parsedata[0]
        for channel, data in zip(self.channels, self._parsedata[1:]):
            data = numpy.array(data, dtype=numpy.float64)
            # filter empty values
            data[data == EIGHTS] = numpy.nan
            data[data == NINES] = numpy.nan
            self.data[channel] = data
        self._parsedata = None

    def parse_comments(self):
        """Parse header values embedded in comments."""
        for comment in self.comments:
            if comment.startswith('DECBAS'):
                # parse DECBAS
                decbas = comment.replace('DECBAS', '').strip()
                self.headers['DECBAS'] = decbas[:decbas.find(' ')]

    def _merge_comments(self, comments):
        """Combine multi-line, period-delimited comments.

        Parameters
        ----------
        comments : array_like
            array of comment strings.

        Returns
        -------
        array_like
            merged comment strings.
        """
        merged = []
        partial = None
        for comment in comments:
            if partial is None:
                partial = comment
            else:
                partial = partial + ' ' + comment
            # comments end with period
            if partial.endswith('.'):
                merged.append(partial)
                partial = None
        # comment that doesn't end in a period
        if partial is not None:
            merged.append(partial)
        return merged
