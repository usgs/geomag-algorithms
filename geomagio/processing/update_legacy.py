import os

from .. import Controller
from ..edge import EdgeFactory
from ..algorithm import FilterAlgorithm
from ..TimeseriesUtility import (
    get_delta_from_interval,
    get_previous_interval,
    get_merged_gaps,
    get_stream_gaps,
)

from datetime import datetime
from obspy.core import UTCDateTime
import typer


def main():
    typer.run(update_legacy)


def update_legacy(
    observatory: str,
    interval: str,
    input_channels: list,
    output_channels: list = None,
    realtime_interval: int = 86400,
    edge_host: str = os.getenv("EDGE_HOST", "cwbpub.cr.usgs.gov "),
    edge_port: int = os.getenv("EDGE_PORT", 2061),
):

    current_time = datetime.utcnow()
    current_time_string = current_time.strftime("%Y-%m-%d")
    endtime = UTCDateTime(current_time_string) - 1

    starttime = endtime - realtime_interval

    timeseries_factory = EdgeFactory(host=edge_host, port=edge_port, interval=interval)

    output_timeseries = timeseries_factory.get_timeseries(
        observatory=observatory,
        starttime=starttime,
        endtime=endtime,
        channels=channels,
        type="variation",
    )

    output_gaps = get_merged_gaps(get_stream_gaps(output_timeseries))

    if len(output_gaps) == 0:
        return

    input_interval = get_previous_interval(interval)
    input_delta = get_delta_from_interval(input_interval)
    output_delta = get_delta_from_interval(interval)

    controller = Controller(
        algorithm=FilterAlgorithm(
            input_sample_period=input_delta, output_sample_period=output_delta
        ),
        inputFactory=EdgeFactory(
            host=edge_host, port=edge_port, interval=input_interval
        ),
        outputFactory=timeseries_factory,
    )

    for output_gap in output_gaps:
        controller.run(
            observatory=(observatory,),
            starttime=output_gap[0],
            endtime=output_gap[1],
            input_channels=input_channels,
            output_channels=output_channels,
        )
