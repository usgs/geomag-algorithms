"""Factory to load IMFV283 files from an input StreamIMFV283Factory."""

from IMFV283Factory import IMFV283Factory
from datetime import datetime
import subprocess
from obspy.core import Stream


class GOESIMFV283Factory(IMFV283Factory):
    """Timeseries Factory for IMFV283 formatted files loaded from the goes
        server.

    Parameters
    ----------
    directory: String
        The directory that support files go in. Primarily criteria files,
        and log files.
    getdcpmessages: String
        The directory where the getDcpMessages executable will be found
    server: array of strings
        An array of strings, to be used in order of which goes server to go to
    user: String
        The goes user.

    Notes
    -----
    GOESIMFV283Factory gets it's data by calling the getDcpMessages program
        provided by NOAA using the subprocess routines.
        https://dcs1.noaa.gov/LRGS/LRGS-Client-Getting-Started.pdf

    The server packets are timestamped when they are received by the server,
    which can easily be 20 minutes off the time of the data. To compensate we
    ask for 30 minutes before and after the range requested.

    See Also
    --------
    IMFV283Factory
    Timeseriesfactory
    """
    def __init__(self, observatory=None, channels=None,
            type=None, interval='minute',  directory=None,
            getdcpmessages=None, server=None, user=None):
        IMFV283Factory.__init__(self, None, observatory, channels,
            type, interval)
        self.directory = directory
        self.getdcpmessages = getdcpmessages
        self.server = server
        self.user = user
        self.log_file_name = self.observatory + '.log'
        self.criteria_file_name = self.observatory + '.sc'

    def get_timeseries(self, starttime, endtime, observatory=None,
            channels=None, type=None, interval=None):
        """Implements get_timeseries

        Notes: Calls IMFV283Factory.parse_string in place of
            IMFV283Factory.get_timeseries.
        """
        observatory = observatory or self.observatory
        channels = channels or self.channels
        type = type or self.type
        interval = interval or self.interval
        timeseries = Stream()
        output = self._retrieve_goes_messages(starttime, endtime, observatory)
        timeseries  += self.parse_string(output)
                # merge channel traces for multiple days
        timeseries.merge()
        # trim to requested start/end time
        timeseries.trim(starttime, endtime)
        self._post_process(timeseries)
        if observatory is not None:
            timeseries = timeseries.select(station=observatory)
        return timeseries

    def _retrieve_goes_messages(self, starttime, endtime, observatory):
        """Retrieve goes messages, using getdcpmessages commandline tool.

        Parameters
        ----------
        starttime: obspy.core.UTCDateTime
            time of first sample.
        endtime: obspy.core.UTCDateTime
            time of last sample.
        observatory: str
            observatory code.

        Notes
        -----
        See page 37-38
            ftp://hazards.cr.usgs.gov/web/geomag-algorithms/DCS Tools Users Guide_4-4.pdf
        getDcpMessages options.
        -h host             A hostname.
        -u user             The user name that must be known to the DDS server
        -f criteria file    The name of the search criteria file.
        -l log file         Logfile name for error messages.
        -t seconds          Timeout value
        -n                  Causes a newline to be output after each messages
        -v                  Causes extra status messages to be output.

        Returns
        -------
        String
            Messages from getDcpMessages
        """

        output = subprocess.check_output(
                [self.getdcpmessages,
                '-h ' + self.server,
                '-u ' + self.user,
                '-f ' + self.directory + '/' + self.criteria_file_name,
                '-l ' + self.directory + '/' + self.log_file_name,
                '-t 60',
                '-n'])
        return output

    def _fill_criteria_file(self, starttime, endtime):
        """Set Criteria Filename

        Notes
        -----
        The Criteria file tells the GOES server what data we want and how
            to return it.
        See Page 30-34:
            ftp://hazards.cr.usgs.gov/web/geomag-algorithms/DCS Tools Users Guide_4-4.pdf

        Sets the criteria filename to the observatory code with a .sc extension
            First 3 lines are comments.
            DAPS_SINCE: The time after which messages are to be retrieved.
            DAPS_UNTIL: The time before which messages are to be retrieved.
            NETWORK_LIST: The file name on the server, which holds the
                key value pairs of observatory keys to be retrieved.
            DAPS_STATUS: Do Not retrieve Status Messages.
            RETRANSMITTED: Do Not retrieve retransmitted messages.
            ASCENDING_TIME: Do Not sort messages into ascending time.
            RT_SETTLE_DELAY: Do wait to prevent duplicate messages.
        """
        start = starttime - 1800
        end = endtime + 1800

        criteria_file = self.directory + '/' + self.criteria_file_name
        buf = []
        buf.append('#\n# LRGS Search Criteria\n#\n')
        buf.append('DAPS_SINCE: ')
        buf.append(starttime.datetime.strftime('%y/%j %H:%M:%S\n'))
        buf.append('DAPS_UNTIL: ')
        buf.append(end.datetime.strftime('%y/%j %H:%M:%S\n'))
        buf.append('NETWORK_LIST: ./opendcs/netlist/' + \
                self.observatory.lower() + \
                '.nl\n')
        buf.append('DAPS_STATUS: N\n')
        buf.append('RETRANSMITTED: N\n')
        buf.append('ASCENDING_TIME: false\n')
        buf.append('RT_SETTLE_DELAY: true\n')

        with open(criteria_file, 'wb') as fh:
            fh.write(''.join(buf))
            fh.close()
