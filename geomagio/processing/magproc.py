from os import path
import os
import sys

from datetime import datetime
from dateutil.relativedelta import relativedelta
from obspy.core import UTCDateTime, Stream
import typer

from ..algorithm.FilterAlgorithm import FilterAlgorithm
from ..edge.EdgeFactory import EdgeFactory
from ..pcdcp import PCDCPFactory, PCDCP_FILE_PATTERN
from ..residual import WebAbsolutesFactory, CalFileFactory

CAL_FILENAME_FORMAT = "{OBSERVATORY}/{OBSERVATORY}{YEAR}PCD.cal"
MIN_TEMPLATE = "%(OBS)s/" + PCDCP_FILE_PATTERN
RAW_TEMPLATE = "%(OBS)s/" + PCDCP_FILE_PATTERN


def main():
    typer.run(prepfiles)


def prepfiles(observatory: str, year: int, month: int):
    month_start = datetime(year, month, 1)
    month_end = month_start + relativedelta(months=1)

    write_cal_file(
        starttime=UTCDateTime(month_start - relativedelta(months=1)),
        endtime=UTCDateTime(month_end + relativedelta(months=1)),
        observatory=observatory,
    )

    timeseries_min, timeseries_sec = gather_data(
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        observatory=observatory,
    )

    write_pcdcp_file(
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        timeseries=timeseries_sec,
        observatory=observatory,
        interval="second",
        base_directory="file://c:/RAW/",
        template=RAW_TEMPLATE,
    )

    write_pcdcp_file(
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        timeseries=timeseries_min,
        observatory=observatory,
        interval="minute",
        base_directory="file://c:/USGSDCP/",
        template=MIN_TEMPLATE,
    )


def write_cal_file(
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    observatory: str,
    base_directory: str = "file://c:/Calibrat/",
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
    # write cal file to specified path
    CalFileFactory().write_file(path=base_directory + filename, readings=readings)


def gather_data(starttime: UTCDateTime, endtime: UTCDateTime, observatory: str):
    f = FilterAlgorithm(input_sample_period=1.0, output_sample_period=60.0)
    f_starttime, f_endtime = f.get_input_interval(starttime, endtime)
    e = EdgeFactory()
    timeseries_sec = e.get_timeseries(
        starttime=f_starttime,
        endtime=f_endtime,
        observatory=observatory,
        channels=["H", "E", "Z", "F"],
        type="variation",
        interval="second",
    )
    return (
        f.process(timeseries_sec),
        timeseries_sec.trim(starttime=starttime, endtime=endtime),
    )


def write_pcdcp_file(
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    timeseries: Stream,
    observatory: str,
    interval: str,
    base_directory: str,
    template: str = PCDCP_FILE_PATTERN,
):
    raw_factory = PCDCPFactory(
        urlInterval=86400, urlTemplate=base_directory + f"{template}",
    )

    raw_factory.put_timeseries(
        timeseries=timeseries,
        starttime=starttime,
        endtime=endtime,
        interval=interval,
        type="variation",
    )
