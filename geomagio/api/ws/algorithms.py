from fastapi import APIRouter, Depends
from starlette.responses import Response

from ... import TimeseriesFactory
from ...algorithm import DbDtAlgorithm
from .DataApiQuery import DataApiQuery
from .data import format_timeseries, get_data_factory, get_data_query, get_timeseries


router = APIRouter()


@router.get("/algorithms/dbdt/")
def get_dbdt(
    query: DataApiQuery = Depends(get_data_query),
    data_factory: TimeseriesFactory = Depends(get_data_factory),
) -> Response:
    dbdt = DbDtAlgorithm()
    # read data
    raw = get_timeseries(data_factory, query)
    # run dbdt
    timeseries = dbdt.process(raw)
    elements = [f"{element}_DT" for element in query.elements]
    # output response
    return format_timeseries(timeseries=timeseries, format=format, elements=elements)
