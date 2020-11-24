import os
from typing import Callable

from ..TimeseriesFactory import TimeseriesFactory
from ..edge import EdgeFactory, MiniSeedFactory


def get_edge_factory(
    data_type="variation", interval="second", **kwargs
) -> TimeseriesFactory:
    return EdgeFactory(
        host=os.getenv("EDGE_HOST", "127.0.0.1"),
        interval=interval,
        type=data_type,
        **kwargs
    )


def get_miniseed_factory(
    data_type="variation", interval="second", **kwargs
) -> TimeseriesFactory:
    return MiniSeedFactory(
        convert_channels=("U", "V", "W"),
        host=os.getenv("EDGE_HOST", "127.0.0.1"),
        interval=interval,
        type=data_type,
        **kwargs
    )
