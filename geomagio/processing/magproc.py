from datetime import datetime
import os
import sys
from typing import List, Tuple

from dateutil.relativedelta import relativedelta
from obspy.core import UTCDateTime, Stream
import typer

from ..algorithm.FilterAlgorithm import FilterAlgorithm
from ..edge import EdgeFactory
from ..pcdcp import PCDCPFactory, PCDCP_FILE_PATTERN
from ..residual import WebAbsolutesFactory, CalFileFactory
from ..Util import get_intervals


CAL_TEMPLATE = "{OBSERVATORY}/{OBSERVATORY}{YEAR}PCD.cal"
PCDCP_TEMPLATE = f"%(OBS)s/{PCDCP_FILE_PATTERN}"


def main():
    """Entrypoint for magproc-prepfiles command defined in setup.py.

    Runs prepfiles() with typer for argument parsing and usage.
    """
    typer.run(prepfiles)


def prepfiles(
    observatory: str,
    year: int,
    month: int,
    # configuration arguments
    calibration_path: str = os.getenv("CALIBRATION_PATH", "file://c:/Calibrat"),
    second_path: str = os.getenv("SECOND_PATH", "file://c:/RAW"),
    minute_path: str = os.getenv("MINUTE_PATH", "file://c:/USGSDCP"),
    temperature_path: str = os.getenv("TEMPERATURE_PATH", "file://c:/DEG"),
    edge_host: str = os.getenv("EDGE_HOST", "cwbpub.cr.usgs.gov"),
):
    month_start = datetime(year, month, 1)
    month_end = month_start + relativedelta(months=1)
    # Calibration data
    write_cal_file(
        starttime=UTCDateTime(month_start - relativedelta(months=1)),
        endtime=UTCDateTime(month_end + relativedelta(months=1)),
        observatory=observatory,
        template="file://" + os.path.join(calibration_path, CAL_TEMPLATE),
    )
    # Variation data
    write_variation_data(
        host=edge_host,
        starttime=UTCDateTime(month_start),
        endtime=UTCDateTime(month_end),
        observatory=observatory,
        second_template="file://" + os.path.join(second_path, PCDCP_TEMPLATE),
        minute_template="file://" + os.path.join(minute_path, PCDCP_TEMPLATE),
    )
    # Temperature data
    # write_temperature_data(
    #     host=edge_host,
    #     starttime=UTCDateTime(month_start),
    #     endtime=UTCDateTime(month_end),
    #     observatory=observatory,
    #     template="file://" + os.path.join(temperature_path, PCDCP_TEMPLATE),
    # )


def write_cal_file(
    starttime: UTCDateTime, endtime: UTCDateTime, observatory: str, template: str,
):
    print(
        f"Loading calibration data for {observatory} [{starttime}, {endtime}]",
        file=sys.stderr,
    )
    url = template.format(OBSERVATORY=observatory, YEAR=starttime.year)
    readings = WebAbsolutesFactory().get_readings(
        observatory=observatory,
        starttime=starttime,
        endtime=endtime,
        include_measurements=True,
    )
    # write cal file to specified path
    CalFileFactory().write_file(url=url, readings=readings)


def write_pcdcp_file(
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    timeseries: Stream,
    observatory: str,
    interval: str,
    channels: List[str],
    template: str = PCDCP_FILE_PATTERN,
):
    PCDCPFactory(urlInterval=86400, urlTemplate=template).put_timeseries(
        timeseries=timeseries,
        starttime=starttime,
        endtime=endtime,
        channels=channels,
        interval=interval,
        type="variation",
    )


def write_temperature_data(
    host: str,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    observatory: str,
    template: str = PCDCP_FILE_PATTERN,
) -> Stream:
    algorithm = FilterAlgorithm(input_sample_period=60.0, output_sample_period=3600.0)
    factory = EdgeFactory(host=host)
    # load minute temperature data
    f_starttime, f_endtime = algorithm.get_input_interval(starttime, endtime)
    print(
        f"Loading minute temperature data for {observatory} [{f_starttime}, {f_endtime}]",
        file=sys.stderr,
    )
    timeseries_temp = factory.get_timeseries(
        starttime=f_starttime,
        endtime=f_endtime,
        observatory=observatory,
        channels=["UK1", "UK2", "UK3", "UK4"],
        type="variation",
        interval="minute",
    )
    # filter to one hour
    print(f"Generating hourly temperature data for {observatory}", file=sys.stderr)
    timeseries_temperature = algorithm.process(timeseries_temp)
    # write data
    write_pcdcp_file(
        starttime=starttime,
        endtime=endtime,
        timeseries=timeseries_temperature,
        observatory=observatory,
        interval="hourly",
        channels=["UK1", "UK2", "UK3", "UK4"],
        template=template,
    )


def write_variation_data(
    host: str,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    observatory: str,
    second_template: str = PCDCP_FILE_PATTERN,
    minute_template: str = PCDCP_FILE_PATTERN,
):
    algorithm = FilterAlgorithm(input_sample_period=1.0, output_sample_period=60.0)
    factory = EdgeFactory(host=host)
    intervals = get_intervals(starttime, endtime)
    for interval in intervals:
        starttime, endtime = interval["start"], interval["end"]
        # load second data
        f_starttime, f_endtime = algorithm.get_input_interval(starttime, endtime)
        print(
            f"Loading second variation data for {observatory} [{f_starttime}, {f_endtime}]",
            file=sys.stderr,
        )
        timeseries_second = factory.get_timeseries(
            starttime=f_starttime,
            endtime=f_endtime,
            observatory=observatory,
            channels=["H", "E", "Z", "F"],
            type="variation",
            interval="second",
        )
        # filter to one minute
        print(
            f"Generating one minute variation data for {observatory} [{starttime}, {endtime}]",
            file=sys.stderr,
        )
        timeseries_minute = algorithm.process(timeseries_second)
        # write files
        write_pcdcp_file(
            starttime=starttime,
            endtime=endtime,
            timeseries=timeseries_second.trim(starttime, endtime),
            observatory=observatory,
            interval="second",
            channels=["H", "E", "Z", "F"],
            template=second_template,
        )
        write_pcdcp_file(
            starttime=starttime,
            endtime=endtime,
            timeseries=timeseries_minute,
            observatory=observatory,
            interval="minute",
            channels=["H", "E", "Z", "F"],
            template=minute_template,
        )
