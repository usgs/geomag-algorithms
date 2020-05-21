import os
from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, Query
from obspy import UTCDateTime, Stream
from starlette.responses import Response

from ...algorithm.DbDtAlgorithm import DbDtAlgorithm
from ... import TimeseriesFactory, TimeseriesUtility
from ...edge import EdgeFactory
from ...iaga2002 import IAGA2002Writer
from ...imfjson import IMFJSONWriter
from .DataApiQuery import (
    DEFAULT_ELEMENTS,
    DataApiQuery,
    DataType,
    OutputFormat,
    SamplingPeriod,
)


def get_data_factory() -> TimeseriesFactory:
    """Reads environment variable to determine the factory to be used

    Returns
    -------
    data_factory
        Edge or miniseed factory object
    """
    data_type = os.getenv("DATA_TYPE", "edge")
    data_host = os.getenv("DATA_HOST", "cwbpub.cr.usgs.gov")
    data_port = int(os.getenv("DATA_PORT", "2060"))
    if data_type == "edge":
        return EdgeFactory(host=data_host, port=data_port)
    else:
        return None


def format_timeseries(
    timeseries: Stream, format: OutputFormat, elements: List[str]
) -> Response:
    """Formats timeseries output

    Parameters
    ----------
    timeseries: data to format
    format: output format
    obspy.core.Stream
        timeseries object with requested data
    """
    if format == OutputFormat.JSON:
        data = IMFJSONWriter.format(timeseries, elements)
        media_type = "application/json"
    else:
        data = IAGA2002Writer.format(timeseries, elements)
        media_type = "text/plain"
    return Response(data, media_type=media_type)


def get_timeseries(data_factory: TimeseriesFactory, query: DataApiQuery) -> Stream:
    """Get timeseries data

    Parameters
    ----------
    data_factory: where to read data
    query: parameters for the data to read
    """

    # gather non-dbdt elements first
    base_elements = [element for element in query.elements if element[1::] != "_DDT"]

    # gather interval
    interval = TimeseriesUtility.get_interval_from_delta(query.sampling_period)
    # get data
    base_timeseries = data_factory.get_timeseries(
        starttime=query.starttime,
        endtime=query.endtime,
        observatory=query.id,
        channels=base_elements,
        type=query.data_type,
        interval=interval,
    )

    if "*_DDT" in query.elements:
        dbdt_elements = [
            element[0:1] for element in query.elements if element[1::] == "_DDT"
        ]

        timeseries = data_factory.get_timeseries(
            starttime=query.starttime,
            endtime=query.endtime,
            observatory=query.id,
            channels=dbdt_elements,
            type=query.data_type,
            interval=interval,
        )

        dbdt_timeseries = DbDtAlgorithm(
            inchannels=dbdt_elements, outchannels=dbdt_elements + "_DDT"
        ).process(timeseries)

        base_timeseries += (trace for trace in dbdt_timeseries)

    return base_timeseries


router = APIRouter()


@router.get("/data/")
def get_data(
    id: str,
    starttime: UTCDateTime = Query(None),
    endtime: UTCDateTime = Query(None),
    elements: List[str] = Query(DEFAULT_ELEMENTS),
    sampling_period: Union[SamplingPeriod, float] = Query(SamplingPeriod.MINUTE),
    data_type: Union[DataType, str] = Query(DataType.ADJUSTED, alias="type"),
    format: OutputFormat = Query(OutputFormat.IAGA2002),
    data_factory: TimeseriesFactory = Depends(get_data_factory),
) -> Response:
    # parse query
    query = DataApiQuery(
        id=id,
        starttime=starttime,
        endtime=endtime,
        elements=elements,
        sampling_period=sampling_period,
        data_type=data_type,
        format=format,
    )
    # read data
    timeseries = get_timeseries(data_factory, query)
    # output response
    return format_timeseries(
        timeseries=timeseries, format=format, elements=query.elements
    )
