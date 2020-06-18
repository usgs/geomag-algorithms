import os
from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, Query
from obspy import UTCDateTime, Stream
from starlette.responses import Response

from ... import TimeseriesFactory, TimeseriesUtility
from ...algorithm import DbDtAlgorithm
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
    # get data
    timeseries = data_factory.get_timeseries(
        starttime=query.starttime,
        endtime=query.endtime,
        observatory=query.id,
        channels=query.elements,
        type=query.data_type,
        interval=TimeseriesUtility.get_interval_from_delta(query.sampling_period),
    )
    return post_process(query, timeseries)


def post_process(query: DataApiQuery, timeseries: Stream) -> Stream:
    """Process timeseries data before it is returned.

    Parameters
    ----------
    query: parameters for the data to read
    timeseries: data that was read
    """
    out = timeseries
    if query.dbdt:
        out = Stream()
        dbdt = Stream()
        for trace in timeseries:
            if trace.stats.channel in query.dbdt:
                dbdt += trace
            else:
                out += trace
        out += DbDtAlgorithm().process(dbdt)
        query.elements = [
            el in query.dbdt and f"{el}_DT" or el for el in query.elements
        ]
    return out


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
    dbdt: List[str] = Query([]),
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
        dbdt=dbdt,
    )
    # read data
    timeseries = get_timeseries(data_factory, query)
    # output response
    return format_timeseries(
        timeseries=timeseries, format=format, elements=query.elements
    )
