import os
from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, Query
from obspy import UTCDateTime, Stream
from starlette.responses import Response

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


def get_data_query(
    id: str = Query(..., title="Observatory code"),
    starttime: UTCDateTime = Query(
        None,
        title="Start Time",
        description="Time of first requested data. Default is start of current UTC day.",
    ),
    endtime: UTCDateTime = Query(
        None,
        title="End Time",
        description="Time of last requested data. Default is starttime plus 24 hours.",
    ),
    elements: List[str] = Query(
        DEFAULT_ELEMENTS,
        title="Geomagnetic Elements.",
        description="Either comma separated list of elements, or repeated query parameter"
        " NOTE: when using 'iaga2002' output format, a maximum of 4 elements is allowed",
    ),
    sampling_period: Union[SamplingPeriod, float] = Query(
        SamplingPeriod.MINUTE,
        title="data rate",
        description="Interval in seconds between values.",
    ),
    data_type: Union[DataType, str] = Query(
        DataType.ADJUSTED,
        alias="type",
        description="Type of data."
        " NOTE: the USGS web service also supports specific EDGE location codes."
        " For example: R0 is 'internet variation'",
    ),
    format: OutputFormat = Query(OutputFormat.IAGA2002),
) -> DataApiQuery:
    """Define query parameters used for webservice requests.

    Uses DataApiQuery for parsing and validation.

    Parameters
    -------
    id
        observatory iaga code
    starttime
        query start
        default is start of current UTC day.
    endtime
        query end
        default is end of current UTC day.
    elements
        geomagnetic elements, or EDGE channel codes
    sampling_period
        data rate
    data_type
        data processing level
    format
        output format
    """
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
    return query


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
    headers = {"allow_origins": "*", "max_age": "86400", "allow_headers": "*"}
    return Response(data, media_type=media_type, headers=headers)


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
    return timeseries


router = APIRouter()


@router.get("/data/")
def get_data(
    query: DataApiQuery = Depends(get_data_query),
    data_factory: TimeseriesFactory = Depends(get_data_factory),
) -> Response:
    # read data
    timeseries = get_timeseries(data_factory, query)
    # output response
    return format_timeseries(
        timeseries=timeseries, format=query.format, elements=query.elements
    )
