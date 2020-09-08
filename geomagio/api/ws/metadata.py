from typing import List

from fastapi import APIRouter, Body, Response
from obspy import UTCDateTime

from ...metadata import Metadata, MetadataCategory
from ..secure.MetadataQuery import MetadataQuery
from ..db import metadata_table

router = APIRouter()


@router.get("/metadata", response_model=List[Metadata])
async def get_metadata(
    category: MetadataCategory = None,
    starttime: UTCDateTime = None,
    endtime: UTCDateTime = None,
    network: str = None,
    station: str = None,
    channel: str = None,
    location: str = None,
    data_valid: bool = None,
    metadata_valid: bool = True,
):
    query = MetadataQuery(
        category=category,
        starttime=starttime,
        endtime=endtime,
        network=network,
        station=station,
        channel=channel,
        location=location,
        data_valid=data_valid,
        metadata_valid=metadata_valid,
    )
    metas = await metadata_table.get_metadata(**query.datetime_dict(exclude={"id"}))
    return metas
