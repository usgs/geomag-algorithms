import sys
from typing import Optional

import numpy
import typer

from ..TimeseriesFactory import TimeseriesFactory
from .factory import get_edge_factory, get_miniseed_factory
from .observatory import adjusted, deltaf, rotate, sqdist_minute
from .obsrio import obsrio_minute, obsrio_second, obsrio_temperatures, obsrio_tenhertz


def main():
    typer.run(process)


def process(
    observatory: str,
    is_obsrio: bool = False,
    adjusted_statefile: Optional[str] = None,
    sqdist_statefile_adjusted: Optional[str] = None,
    sqdist_statefile_variation: Optional[str] = None,
):
    print(
        f"Processing observatory {observatory} (is_obsrio={is_obsrio})", file=sys.stderr
    )
    if is_obsrio:
        process_obsrio(observatory=observatory)
    process_variation(observatory=observatory, interval="second")
    process_variation(
        interval="minute",
        observatory=observatory,
        sqdist_statefile=sqdist_statefile_variation,
    )
    if adjusted_statefile is not None:
        process_adjusted(
            adjusted_statefile=adjusted_statefile,
            interval="second",
            observatory=observatory,
        )
        process_adjusted(
            adjusted_statefile=adjusted_statefile,
            interval="minute",
            observatory=observatory,
            sqdist_statefile=sqdist_statefile_adjusted,
        )


def process_adjusted(
    observatory: str,
    adjusted_statefile: Optional[str] = None,
    adjusted_matrix: Optional[numpy.ndarray] = None,
    adjusted_pier_correction: Optional[float] = None,
    input_factory: Optional[TimeseriesFactory] = None,
    interval: str = "second",
    output_factory: Optional[TimeseriesFactory] = None,
    output_factory_extras: Optional[TimeseriesFactory] = None,
    sqdist_statefile: Optional[str] = None,
):
    input_factory = input_factory or get_edge_factory(data_type="variation")
    output_factory = output_factory or get_edge_factory(data_type="adjusted")
    # optional separate output factory for G, H, D (for iaga2002...)
    output_factory_extras = output_factory_extras or output_factory
    adjusted(
        input_factory=input_factory,
        interval=interval,
        observatory=observatory,
        output_factory=output_factory,
        matrix=adjusted_matrix,
        pier_correction=adjusted_pier_correction,
        statefile=adjusted_statefile,
    )
    # compute delta f
    deltaf(
        deltaf_from="geo",
        input_factory=output_factory,
        interval=interval,
        observatory=observatory,
        output_factory=output_factory_extras,
    )
    # h,d based on adjusted
    rotate(
        observatory=observatory,
        input_factory=output_factory,
        interval=interval,
        output_channels=("H", "D"),
        output_factory=output_factory_extras,
        xyz_from="geo",
        xyz_to="mag",
    )
    if interval == "minute" and sqdist_statefile is not None:
        sqdist_minute(
            input_factory=output_factory,
            observatory=observatory,
            output_factory=output_factory,
            statefile=sqdist_statefile,
        )


def process_obsrio(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    output_factory: Optional[TimeseriesFactory] = None,
):
    input_factory = input_factory or get_miniseed_factory(data_type="variation")
    output_factory = output_factory or get_edge_factory(data_type="variation")
    # filter to 1hz H,E,Z
    obsrio_tenhertz(
        observatory=observatory,
        input_factory=input_factory,
        output_factory=output_factory,
    )
    # copy 1hz f
    obsrio_second(
        observatory=observatory,
        input_factory=input_factory,
        output_factory=output_factory,
    )
    # filter to 1m (processes 1s in output_factory)
    obsrio_minute(
        observatory=observatory,
        input_factory=output_factory,
        output_factory=output_factory,
    )
    # filter temperatures to 1m
    obsrio_temperatures(
        observatory=observatory,
        input_factory=input_factory,
        output_factory=output_factory,
    )


def process_variation(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    interval: str = "second",
    output_factory: Optional[TimeseriesFactory] = None,
    sqdist_statefile: Optional[str] = None,
):
    input_factory = input_factory or get_edge_factory(data_type="variation")
    output_factory = output_factory or get_edge_factory(data_type="variation")
    # compute delta f
    deltaf(
        deltaf_from="obs",
        input_factory=input_factory,
        interval=interval,
        observatory=observatory,
        output_factory=output_factory,
    )
    # x,y based on declination baseline
    rotate(
        observatory=observatory,
        input_factory=input_factory,
        interval=interval,
        output_channels=("X", "Y"),
        output_factory=output_factory,
        xyz_from="obs",
        xyz_to="geo",
    )
    # d based on h,e
    rotate(
        input_factory=input_factory,
        interval=interval,
        observatory=observatory,
        output_channels=("D",),
        output_factory=output_factory,
        xyz_from="obs",
        xyz_to="obsd",
    )
    if interval == "minute" and sqdist_statefile is not None:
        sqdist_minute(
            input_factory=input_factory,
            observatory=observatory,
            output_factory=output_factory,
            statefile=sqdist_statefile,
        )


if __name__ == "__main__":
    main()
