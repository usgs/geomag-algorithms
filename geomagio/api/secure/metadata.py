"""Module for metadata service.

Uses login.py for user management.

Anyone can access metadata.
Logged in users can create new metadata.
Update and delete are restricted based on group membership.


Configuration:
    uses environment variables:

    ADMIN_GROUP           - delete is restricted the admin group.
    REVIEWER_GROUP        - update is restricted the reviewer group.
"""
import os
from typing import List

from fastapi import APIRouter, Body, Depends, Request, Response
from obspy import UTCDateTime

from ...metadata import Metadata, MetadataCategory
from ..db import metadata_table
from .login import require_user, User
from .MetadataQuery import MetadataQuery
from ... import pydantic_utcdatetime

# routes for login/logout
router = APIRouter()


@router.post("/metadata", response_model=Metadata)
async def create_metadata(
    request: Request,
    metadata: Metadata,
    user: User = Depends(require_user()),
):
    metadata = await metadata_table.create_metadata(metadata)
    return Response(metadata, status_code=201, media_type="application/json")


@router.delete("/metadata/{id}")
async def delete_metadata(
    id: int, user: User = Depends(require_user(os.getenv("ADMIN_GROUP", "admin")))
):
    await metadata_table.delete_metadata(id)


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


@router.get("/metadata/{id}", response_model=Metadata)
async def get_metadata_by_id(id: int):
    meta = await metadata_table.get_metadata(id=id)
    if len(meta) != 1:
        return Response(status_code=404)
    else:
        return meta[0]


@router.put("/metadata/{id}")
async def update_metadata(
    id: int,
    metadata: Metadata = Body(...),
    user: User = Depends(require_user([os.getenv("REVIEWER_GROUP", "reviewer")])),
):
    await metadata_table.update_metadata(metadata)
