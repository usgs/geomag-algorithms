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
from geomagio.pcdcp.PCDCPFactory import PCDCPFactory, PCDCP_FILE_PATTERN
from geomagio.edge.EdgeFactory import EdgeFactory

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
MONTH = int(sys.argv[3])

starttime = datetime(YEAR, MONTH, 1)
endtime = starttime + relativedelta(months=+1)
cal_starttime = starttime + relativedelta(months=-1)
cal_endtime = endtime + relativedelta(months=+2)

starttime = UTCDateTime(year=starttime.year, month=starttime.month, day=starttime.day)
endtime = UTCDateTime(year=endtime.year, month=endtime.month, day=endtime.day)
cal_starttime = UTCDateTime(
    year=cal_starttime.year, month=cal_starttime.month, day=cal_starttime.day
)
cal_endtime = UTCDateTime(
    year=cal_endtime.year, month=cal_endtime.month, day=cal_endtime.day
)


filename = CAL_FILENAME_FORMAT.format(OBSERVATORY=OBSERVATORY, YEAR=cal_starttime.year)
cal_file_path = "file://c:/Calibrat/{}/".format(OBSERVATORY)
readings = WebAbsolutesFactory().get_readings(
    observatory=OBSERVATORY,
    starttime=cal_starttime,
    endtime=cal_endtime,
    include_measurements=True,
)

calfile = CalFileFactory().format_readings(readings=readings)

channels = ["H", "E", "Z", "F"]

edge_factory = EdgeFactory()
raw_timeseries = edge_factory.get_timeseries(
    observatory=OBSERVATORY,
    starttime=starttime,
    endtime=endtime,
    channels=channels,
    interval="second",
    type="variation",
)

min_timeseries = edge_factory.get_timeseries(
    observatory=OBSERVATORY,
    starttime=starttime,
    endtime=endtime,
    channels=channels,
    interval="minute",
    type="variation",
)

RAW_TEMPLATE = "file://c:/RAW/%(OBS)s/" + PCDCP_FILE_PATTERN
MIN_TEMPLATE = "file://c:/USGSDCP/%(OBS)s/" + PCDCP_FILE_PATTERN

raw_factory = PCDCPFactory(
    observatory=OBSERVATORY,
    channels=channels,
    type="variation",
    interval="second",
    urlInterval=86400,
    urlTemplate=f"file://{RAW_TEMPLATE}",
)

raw_factory.put_timeseries(
    timeseries=raw_timeseries,
    starttime=starttime,
    endtime=endtime,
    interval="second",
    type="variation",
    channels=channels,
)

min_factory = PCDCPFactory(
    observatory=OBSERVATORY,
    channels=channels,
    type="variation",
    interval="minute",
    urlInterval=86400,
    urlTemplate=f"file://{MIN_TEMPLATE}",
)

min_factory.put_timeseries(
    timeseries=min_timeseries,
    starttime=starttime,
    endtime=endtime,
    interval="minute",
    type="variation",
    channels=channels,
)
