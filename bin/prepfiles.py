from __future__ import absolute_import

from datetime import datetime
from dateutil.relativedelta import relativedelta
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

PCDCP_FILENAME_FORMAT = "{OBSERVATORY}{YEAR}{YEARDAY}"
CAL_FILENAME_FORMAT = "{OBSERVATORY}{YEAR}PCD.cal"

if len(sys.argv) != 4:
    cmd = sys.argv[0]
    print("Usage:  {} OBSERVATORY YEAR YEARDAY".format(cmd), file=sys.stderr)
    print(
        "Example:  {} HON 2019 325".format(cmd), file=sys.stderr,
    )
    sys.exit(1)

OBSERVATORY = sys.argv[1]
YEAR = int(sys.argv[2])
YEARDAY = int(sys.argv[3])

pcdcp_starttime = datetime(YEAR, 1, 1) + relativedelta(days=+YEARDAY - 1)
pcdcp_endtime = pcdcp_starttime + relativedelta(days=+1)
cal_starttime = pcdcp_starttime + relativedelta(months=-1)
cal_endtime = pcdcp_starttime + relativedelta(months=+2)
pcdcp_starttime = UTCDateTime(
    "{}-{}-{}T00:00:00".format(
        pcdcp_starttime.year, pcdcp_starttime.month, pcdcp_starttime.day
    )
)
pcdcp_endtime = UTCDateTime(
    "{}-{}-{}T00:00:00".format(
        pcdcp_endtime.year, pcdcp_endtime.month, pcdcp_endtime.day
    )
)
cal_starttime = UTCDateTime(
    "{}-{}-{}T00:00:00".format(
        cal_starttime.year, cal_starttime.month, cal_starttime.day
    )
)
cal_endtime = UTCDateTime(
    "{}-{}-{}T00:00:00".format(cal_endtime.year, cal_endtime.month, cal_endtime.day)
)


filename = CAL_FILENAME_FORMAT.format(OBSERVATORY=OBSERVATORY, YEAR=cal_starttime.year)
cal_file_path = ":C\\Calibrat\\{}\\".format(OBSERVATORY)
readings = WebAbsolutesFactory().get_readings(
    observatory=OBSERVATORY,
    starttime=cal_starttime,
    endtime=cal_endtime,
    include_measurements=True,
)

calfile = CalFileFactory().format_readings(readings=readings)

print("Writing cal file to {}".format(filename), file=sys.stderr)
with open(cal_file_path + filename, "wb", -1) as f:
    f.write(calfile.encode())

pcdcp_channels = ["H", "E", "Z", "F"]


e = EdgeFactory()
ts_second = e.get_timeseries(
    starttime=pcdcp_starttime,
    endtime=pcdcp_endtime,
    observatory=OBSERVATORY,
    channels=pcdcp_channels,
    type="variation",
    interval="second",
)
ts_minute = e.get_timeseries(
    starttime=pcdcp_starttime,
    endtime=pcdcp_endtime,
    observatory=OBSERVATORY,
    channels=pcdcp_channels,
    type="variation",
    interval="minute",
)

pcdcp_w = PCDCPWriter()
raw_file_path = ":C\\RAW\\{}\\".format(OBSERVATORY)
raw_filename = (
    PCDCP_FILENAME_FORMAT.format(
        OBSERVATORY=OBSERVATORY, YEAR=pcdcp_starttime.year, YEARDAY=YEARDAY
    )
    + ".raw"
)
min_file_path = ":C\\USGSDCP\\{}\\".format(OBSERVATORY)
min_filename = (
    PCDCP_FILENAME_FORMAT.format(
        OBSERVATORY=OBSERVATORY, YEAR=pcdcp_starttime.year, YEARDAY=YEARDAY
    )
    + ".min"
)
print("Writing raw file to {}".format(raw_filename), file=sys.stderr)
raw_file = open(raw_file_path + raw_filename, "wb")
pcdcp_w.write(raw_file, ts_second, pcdcp_channels)
raw_file.close()
print("Writing min file to {}".format(min_filename), file=sys.stderr)
min_file = open(min_file_path + min_filename, "wb")
pcdcp_w.write(min_file, ts_minute, pcdcp_channels)
min_file.close()
