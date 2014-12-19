
from os import path
# ensure geomag is on the path before importing
script_dir = path.dirname(path.abspath(__file__))
if __file__ != 'main.py':
    import sys
    sys.path.append(script_dir)

import geomag.io.iaga2002 as iaga2002
from obspy.core.utcdatetime import UTCDateTime


def main():
    """Example loading IAGA2002 test data from a directory."""
    iaga_dir = path.normpath(path.join(script_dir, '../../etc/iaga2002'))
    factory = iaga2002.IAGA2002Factory('file://' + iaga_dir +
            '/%(OBS)s/%(interval)s%(type)s/%(obs)s%(ymd)s%(t)s%(i)s.%(i)s',
            observatory='BOU', channels=('H', 'D', 'Z', 'F'),
            interval='minute', type='variation')
    timeseries = factory.get_timeseries(
            UTCDateTime('2014-11-01'), UTCDateTime('2014-11-02'))
    print timeseries


if __name__ == '__main__':
    main()
