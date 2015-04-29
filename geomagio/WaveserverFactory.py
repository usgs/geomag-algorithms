"""
Access timeseries from an Earthworm waveserver.
"""

from obspy.core.utcdatetime import UTCDateTime
from obspy import earthworm


class WaveserverFactory(object):
    """
    Access timeseries from an Earthworm waveserver.
    """

    def __init__(self, host, port):
        self.client = earthworm.Client(host, port)

    def get_timeseries(
            self, observatory, starttime, endtime,
            channels=('MVH', 'MVE', 'MVZ'), location='R0', network='NT'):
        """
        Get timeseries for an observatory.
        """
        client = self.client
        stream = None
        for channel in channels:
            data = client.getWaveform(
                    network, observatory, location, channel,
                    starttime, endtime)
            if stream is None:
                stream = data
            else:
                stream += data
        return stream


def main():
    """
    main method to test waveserver factory
    """
    factory = WaveserverFactory('136.177.50.84', 2060)
    starttime = UTCDateTime(2014, 6, 12, 5, 0, 0)
    endtime = UTCDateTime(2014, 6, 12, 5, 30, 0)
    result = factory.get_timeseries('BOU', starttime=starttime,
            endtime=endtime, location='R0')
    # result += f.getTimeseries('BOU', starttime, endtime, 'R1')
    result.plot()

if __name__ == '__main__':
    main()
