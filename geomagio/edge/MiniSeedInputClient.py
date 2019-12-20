from __future__ import absolute_import, print_function
import io
import socket
import sys


class MiniSeedInputClient(object):
    """Client to write MiniSeed formatted data to Edge.

    Connects on first call to send().
    Use close() to disconnect.

    Parameters
    ----------
    host: str
        MiniSeedServer hostname
    port: int
        MiniSeedServer port
    """
    def __init__(self, host, port=2061):
        self.host = host
        self.port = port
        self.socket = None

    def close(self):
        """Close socket if open.
        """
        if self.socket is not None:
            try:
                self.socket.close()
            finally:
                self.socket = None

    def connect(self, max_attempts=2):
        """Connect to socket if not already open.

        Parameters
        ----------
        max_attempts: int
            number of times to try connecting when there are failures.
            default 2.
        """
        if self.socket is not None:
            return
        s = None
        attempts = 0
        while True:
            attempts += 1
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(self.host, self.port)
                break
            except socket.error as e:
                if attempts >= max_attempts:
                    raise
                print('Unable to connect (%s), trying again' % e,
                        file=sys.stderr)
        self.socket = s

    def send(self, stream):
        """Send traces to EDGE in miniseed format.

        All traces in stream will be converted to MiniSeed, and sent as-is.

        Parameters
        ----------
        stream: obspy.core.Stream
            stream with trace(s) to send.
        """
        # connect if needed
        if self.socket is None:
            self.connect()
        # convert stream to miniseed
        buf = io.BytesIO()
        stream.write(buf, format='MSEED')
        # send data
        self.socket.sendall(buf)
