from os import path
import os
import sys

from datetime import datetime
from dateutil.relativedelta import relativedelta
from obspy.core import UTCDateTime
import typer

from ..edge.EdgeFactory import EdgeFactory
from ..pcdcp import PCDCPFactory, PCDCP_FILE_PATTERN
from ..residual import WebAbsolutesFactory, CalFileFactory

CAL_FILENAME_FORMAT = "{OBSERVATORY}/{OBSERVATORY}{YEAR}PCD.cal"
MIN_TEMPLATE = "file://c:/USGSDCP/%(OBS)s/" + PCDCP_FILE_PATTERN
RAW_TEMPLATE = "%(OBS)s/" + PCDCP_FILE_PATTERN


def main():
    typer.run(prepfiles)


def prepfiles(observatory: str, year: int, month: int):
    starttime = datetime(year, month, 1)
    endtime = starttime + relativedelta(months=+1)

    write_cal_file(starttime, endtime, observatory)


def write_cal_file(
    starttime, endtime, observatory, base_directory="file://c:/Calibrat/"
):
    filename = CAL_FILENAME_FORMAT.format(OBSERVATORY=observatory, YEAR=starttime.year)
    starttime = starttime + relativedelta(months=-1)
    endtime = endtime + relativedelta(months=+2)
    starttime = UTCDateTime(
        year=starttime.year, month=starttime.month, day=starttime.day
    )
    endtime = UTCDateTime(year=endtime.year, month=endtime.month, day=endtime.day)
    filename = CAL_FILENAME_FORMAT.format(OBSERVATORY=observatory, YEAR=starttime.year)
    readings = WebAbsolutesFactory().get_readings(
        observatory=observatory,
        starttime=starttime,
        endtime=endtime,
        include_measurements=True,
    )

    calfile = CalFileFactory().format_readings(readings=readings)

    with open(base_directory + filename, "wb") as f:
        f.write(calfile)


def write_raw_file(starttime, endtime, observatory, base_directory="file://c:/RAW/"):
    starttime = UTCDateTime(
        year=starttime.year, month=starttime.month, day=starttime.day
    )
    endtime = UTCDateTime(year=endtime.year, month=endtime.month, day=endtime.day)

    channels = ["H", "E", "Z", "F"]

    edge_factory = EdgeFactory()
    raw_timeseries = edge_factory.get_timeseries(
        observatory=observatory,
        starttime=starttime,
        endtime=endtime,
        channels=channels,
        interval="second",
        type="variation",
    )

    raw_factory = PCDCPFactory(
        observatory=observatory,
        channels=channels,
        type="variation",
        interval="second",
        urlInterval=86400,
        urlTemplate=base_directory + f"{RAW_TEMPLATE}",
    )

    raw_factory.put_timeseries(
        timeseries=raw_timeseries,
        starttime=starttime,
        endtime=endtime,
        interval="second",
        type="variation",
        channels=channels,
    )


def write_min_file(starttime, endtime, observatory, base_directory="file://c:/MIN/"):
    starttime = UTCDateTime(
        year=starttime.year, month=starttime.month, day=starttime.day
    )
    endtime = UTCDateTime(year=endtime.year, month=endtime.month, day=endtime.day)

    channels = ["H", "E", "Z", "F"]

    min_timeseries = EdgeFactory().get_timeseries(
        observatory=observatory,
        starttime=starttime,
        endtime=endtime,
        channels=channels,
        interval="minute",
        type="variation",
    )

    min_factory = PCDCPFactory(
        observatory=observatory,
        channels=channels,
        type="variation",
        interval="minute",
        urlInterval=86400,
        urlTemplate=base_directory + f"{MIN_TEMPLATE}",
    )

    min_factory.put_timeseries(
        timeseries=min_timeseries,
        starttime=starttime,
        endtime=endtime,
        interval="minute",
        type="variation",
        channels=channels,
    )
