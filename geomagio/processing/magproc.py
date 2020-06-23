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
HOR_TEMPLATE = "%(OBS)s/" + PCDCP_FILE_PATTERN


def main():
    typer.run(prepfiles)


def prepfiles(observatory: str, year: int, month: int):
    month_start = datetime(year, month, 1)
    month_end = month_start + relativedelta(months=1)

    write_cal_file(
        starttime=UTCDateTime(month_start - relativedelta(months=1)),
        endtime=UTCDateTime(month_end + relativedelta(months=1)),
        observatory=observatory,
        base_directory=os.getenv("RAW_DIRECTORY", "file://c:/Calibrat"),
    )

    timeseries_hor, timeseries_min, timeseries_sec = gather_data(
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        observatory=observatory,
    )

    basedir = os.getenv("RAW_DIRECTORY", "file://c:/RAW")

    write_pcdcp_file(
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        timeseries=timeseries_sec,
        observatory=observatory,
        interval="second",
        base_directory=basedir,
        template=os.path.join(basedir, RAW_TEMPLATE),
    )

    basedir = os.getenv("RAW_DIRECTORY", "file://c:/USGSDCP")

    write_pcdcp_file(
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        timeseries=timeseries_min,
        observatory=observatory,
        interval="minute",
        base_directory=basedir,
        template=os.path.join(basedir, MIN_TEMPLATE),
    )

    basedir = os.getenv("RAW_DIRECTORY", "file://c:/DEG")

    write_pcdcp_file(
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        timeseries=timeseries_hor,
        observatory=observatory,
        interval="hourly",
        base_directory=basedir,
        template=os.path.join(basedir, HOR_TEMPLATE),
    )


def write_cal_file(
    starttime: UTCDateTime, endtime: UTCDateTime, observatory: str, base_directory: str,
):
    filename = CAL_FILENAME_FORMAT.format(OBSERVATORY=observatory, YEAR=starttime.year)
    readings = WebAbsolutesFactory().get_readings(
        observatory=observatory,
        starttime=starttime,
        endtime=endtime,
        include_measurements=True,
    )
    # write cal file to specified path
    CalFileFactory().write_file(
        path=os.path.join(base_directory, filename), readings=readings
    )


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
    timeseries_min = f.process(timeseries_sec)
    f = FilterAlgorithm(input_sample_period=60.0, output_sample_period=3600.0)
    f_starttime, f_endtime = f.get_input_interval(starttime, endtime)
    timeseries_temp = e.get_timeseries(
        starttime=f_starttime,
        endtime=f_endtime,
        observatory=observatory,
        channels=["G", "UK1", "UK2", "UK3", "UK4"],
        type="variation",
        interval="minute",
    )
    timeseries_hor = f.process(timeseries_temp)

    return (
        timeseries_hor,
        timeseries_min,
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
        urlInterval=86400, urlTemplate=base_directory + template,
    ).put_timeseries(
        timeseries=timeseries,
        starttime=starttime,
        endtime=endtime,
        interval=interval,
        type="variation",
    )
