from __future__ import absolute_import

import sys
from os import path
import os
from obspy.core import UTCDateTime

# ensure geomag is on the path before importing
try:
    import geomagio  # noqa (ignores this line for lint purposes.)
except ImportError:
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, "..")))

from geomagio.residual import WebAbsolutesFactory, CalFileFactory
from geomagio.edge import EdgeFactory
from geomagio.pcdcp import PCDCPWriter

FILENAME_FORMAT = "./{OBSERVATORY}{YEAR}{MONTH}"

if len(sys.argv) != 4:
    cmd = sys.argv[0]
    print("Usage:  {} OBSERVATORY YEAR MONTH".format(cmd), file=sys.stderr)
    print(
        "Example:  {} HON 2019 11".format(cmd), file=sys.stderr,
    )
    sys.exit(1)

OBSERVATORY = sys.argv[1]
YEAR = sys.argv[2]
MONTH = sys.argv[3]

starttime = UTCDateTime("{}-{}-01T00:00:00".format(YEAR, MONTH))
end_month = starttime.month + 1
if end_month == 13:
    end_month = "01"
    YEAR += 1
endtime = UTCDateTime("{}-{}-01T00:00:00".format(YEAR, end_month))

filename = FILENAME_FORMAT.format(
    OBSERVATORY=OBSERVATORY, YEAR=starttime.year, MONTH=starttime.month
)

readings = WebAbsolutesFactory().get_readings(
    observatory=OBSERVATORY,
    starttime=starttime,
    endtime=endtime,
    include_measurements=True,
)

calfile = CalFileFactory().format_readings(readings=readings)

print("Writing cal file to {}".format(filename), file=sys.stderr)
with open(filename + "WebAbsMaster.cal", "wb", -1) as f:
    f.write(calfile.encode())

pcdcp_channels = ["H", "E", "Z", "F"]

e = EdgeFactory()
ts_second = e.get_timeseries(
    starttime=starttime,
    endtime=endtime,
    observatory=OBSERVATORY,
    channels=pcdcp_channels,
    type="variation",
    interval="second",
)
ts_minute = e.get_timeseries(
    starttime=starttime,
    endtime=endtime,
    observatory=OBSERVATORY,
    channels=pcdcp_channels,
    type="variation",
    interval="minute",
)

pcdcp_w = PCDCPWriter()
print("Writing raw file to {}".format(filename), file=sys.stderr)
sec_file = open(filename + ".raw", "wb")
pcdcp_w.write(sec_file, ts_second, pcdcp_channels)
sec_file.close()
print("Writing min file to {}".format(filename), file=sys.stderr)
min_file = open(filename + ".min", "wb")
pcdcp_w.write(min_file, ts_minute, pcdcp_channels)
min_file.close()
