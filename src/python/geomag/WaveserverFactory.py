#! /usr/bin/env python

import sys
from obspy.core.utcdatetime import UTCDateTime
from obspy.earthworm import Client


class WaveserverFactory(object):
  def __init__(self, host, port):
    self.client = Client(host, port)
  # get timeseries for an observatory
  def getTimeseries(self, observatory, starttime, endtime, location='R0'):
    c = self.client
    st = c.getWaveform('NT', observatory, location, 'MVH', starttime, endtime)
    st += c.getWaveform('NT', observatory, location, 'MVE', starttime, endtime)
    st += c.getWaveform('NT', observatory, location, 'MVZ', starttime, endtime)
    return st


if __name__ == '__main__':
  f = WaveserverFactory('136.177.50.84', 2060)
  starttime = UTCDateTime(2014, 6, 12, 5, 0, 0)
  endtime = UTCDateTime(2014, 6, 12, 5, 30, 0)
  result = f.getTimeseries('BOU', starttime, endtime, 'R0')
  #result += f.getTimeseries('BOU', starttime, endtime, 'R1')
  print result
  result.plot()
