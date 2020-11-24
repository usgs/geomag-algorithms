import os
from typing import Optional

import numpy

from ..algorithm import (
    Algorithm,
    AdjustedAlgorithm,
    DeltaFAlgorithm,
    SqDistAlgorithm,
    XYZAlgorithm,
)
from ..edge import EdgeFactory, MiniSeedFactory
from ..Controller import Controller, get_realtime_interval
from ..TimeseriesFactory import TimeseriesFactory
from .factory import get_edge_factory


def adjusted(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    interval: str = "second",
    output_factory: Optional[TimeseriesFactory] = None,
    matrix: Optional[numpy.ndarray] = None,
    pier_correction: Optional[float] = None,
    statefile: Optional[str] = None,
    realtime_interval: int = 600,
):
    """Run Adjusted algorithm.

    Parameters
    ----------
    observatory: observatory to calculate
    input_factory: where to read, should be configured with data_type
    interval: data interval
    output_factory: where to write, should be configured with data_type
    matrix: adjusted matrix
    pier_correction: adjusted pier correction
    statefile: adjusted statefile
    realtime_interval: window in seconds

    Uses update_limit=10.
    """
    if not statefile and (not matrix or not pier_correction):
        raise ValueError("Either statefile or matrix and pier_correction are required.")
    starttime, endtime = get_realtime_interval(realtime_interval)
    controller = Controller(
        algorithm=AdjustedAlgorithm(
            matrix=matrix,
            pier_correction=pier_correction,
            statefile=statefile,
            data_type="adjusted",
            location="A0",
        ),
        inputFactory=input_factory or get_edge_factory(data_type="variation"),
        inputInterval=interval,
        outputFactory=output_factory or get_edge_factory(data_type="adjusted"),
        outputInterval=interval,
    )
    controller.run_as_update(
        observatory=(observatory,),
        output_observatory=(observatory,),
        starttime=starttime,
        endtime=endtime,
        input_channels=("H", "E", "Z", "F"),
        output_channels=("X", "Y", "Z", "F"),
        realtime=realtime_interval,
        update_limit=10,
    )


def deltaf(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    interval: str = "second",
    output_factory: Optional[TimeseriesFactory] = None,
    deltaf_from="obs",
    realtime_interval: int = 600,
):
    """Run Delta-F algorithm.

    Parameters
    ----------
    observatory: observatory to calculate
    input_factory: where to read, should be configured with data_type and interval
    output_factory: where to write, should be configured with data_type and interval
    deltaf_from: one of {"obs", "mag", "geo"}
    realtime_interval: window in seconds

    Uses update_limit=10.
    """
    starttime, endtime = get_realtime_interval(realtime_interval)
    controller = Controller(
        algorithm=DeltaFAlgorithm(informat=deltaf_from),
        inputFactory=input_factory or get_edge_factory(),
        inputInterval=interval,
        outputFactory=output_factory or get_edge_factory(),
        outputInterval=interval,
    )
    controller.run_as_update(
        observatory=(observatory,),
        output_observatory=(observatory,),
        starttime=starttime,
        endtime=endtime,
        output_channels=("G",),
        realtime=realtime_interval,
        update_limit=10,
    )


def rotate(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    interval: str = "second",
    output_channels=("X", "Y"),
    output_factory: Optional[TimeseriesFactory] = None,
    realtime_interval: int = 600,
    xyz_from="obs",
    xyz_to="geo",
):
    """Run XYZ rotation algorithm.

    Parameters
    ----------
    observatory: observatory to calculate
    input_factory: where to read, should be configured with data_type and interval
    output_channels: which channels to write
    output_factory: where to write, should be configured with data_type and interval
    realtime_interval: window in seconds
    xyz_from: one of {"obs", "mag", "geo"}
    xyz_to: one of {"obs", "obsd", "mag", "geo"}

    Uses update_limit=10.
    """
    starttime, endtime = get_realtime_interval(realtime_interval)
    controller = Controller(
        algorithm=XYZAlgorithm(informat=xyz_from, outformat=xyz_to),
        inputFactory=input_factory or get_edge_factory(),
        inputInterval=interval,
        outputFactory=output_factory or get_edge_factory(),
        outputInterval=interval,
    )
    controller.run_as_update(
        observatory=(observatory,),
        output_observatory=(observatory,),
        starttime=starttime,
        endtime=endtime,
        output_channels=output_channels,
        realtime=realtime_interval,
        update_limit=10,
    )


def sqdist_minute(
    observatory: str,
    statefile: str,
    input_factory: Optional[TimeseriesFactory] = None,
    output_factory: Optional[TimeseriesFactory] = None,
    realtime_interval: int = 1800,
):
    """Run SqDist algorithm.

    Only supports "minute" interval.

    Parameters
    ----------
    observatory: observatory to calculate
    statefile: sqdist statefile must already exist
    input_factory: where to read, should be configured with data_type and interval
    output_factory: where to write, should be configured with data_type and interval
    realtime_interval: window in seconds
    """
    if not statefile:
        raise ValueError("Statefile is required.")
    starttime, endtime = get_realtime_interval(realtime_interval)
    controller = Controller(
        algorithm=SqDistAlgorithm(
            alpha=2.3148e-5,
            gamma=3.3333e-2,
            m=1440,
            mag=True,
            smooth=180,
            statefile=statefile,
        ),
        inputFactory=input_factory or get_edge_factory(interval="minute"),
        inputInterval="minute",
        outputFactory=output_factory or get_edge_factory(interval="minute"),
        outputInterval="minute",
    )
    # sqdist is stateful, use run
    controller.run(
        observatory=(observatory,),
        output_observatory=(observatory,),
        starttime=starttime,
        endtime=endtime,
        input_channels=("X", "Y", "Z", "F"),
        output_channels=("MDT", "MSQ", "MSV"),
        realtime=realtime_interval,
        rename_output_channel=(("H_Dist", "MDT"), ("H_SQ", "MSQ"), ("H_SV", "MSV")),
        update_limit=10,
    )
