import datetime
import enum

from obspy import UTCDateTime
from sqlalchemy import or_, Boolean, Column, Index, Integer, String, Table, Text
import sqlalchemy_utc

from ...metadata import Metadata, MetadataCategory
from .common import database, sqlalchemy_metadata


"""Metadata database model.

See pydantic model geomagio.metadata.Metadata
"""
metadata = Table(
    "metadata",
    sqlalchemy_metadata,
    ## COLUMNS
    Column("id", Integer, primary_key=True),
    # author
    Column("created_by", String(length=255), index=True),
    Column(
        "created_time",
        sqlalchemy_utc.UtcDateTime,
        default=sqlalchemy_utc.now,
        index=True,
    ),
    # reviewer
    Column("reviewed_by", String(length=255), index=True, nullable=True),
    Column("reviewed_time", sqlalchemy_utc.UtcDateTime, index=True, nullable=True),
    # time range
    Column("starttime", sqlalchemy_utc.UtcDateTime, index=True, nullable=True),
    Column("endtime", sqlalchemy_utc.UtcDateTime, index=True, nullable=True),
    # what data metadata references, null for wildcard
    Column("network", String(length=255), nullable=True),  # indexed below
    Column("station", String(length=255), nullable=True),  # indexed below
    Column("channel", String(length=255), nullable=True),  # indexed below
    Column("location", String(length=255), nullable=True),  # indexed below
    # category (flag, matrix, etc)
    Column("category", String(length=255)),  # indexed below
    # higher priority overrides lower priority
    Column("priority", Integer, default=1),
    # whether data is valid (primarily for flags)
    Column("data_valid", Boolean, default=True, index=True),
    # whether metadata is valid (based on review)
    Column("metadata_valid", Boolean, default=True, index=True),
    # metadata json blob
    Column("metadata", Text, nullable=True),
    # general comment
    Column("comment", Text, nullable=True),
    # review specific comment
    Column("review_comment", Text, nullable=True),
    ## INDICES
    Index(
        "index_station_metadata",
        # sncl
        "network",
        "station",
        "channel",
        "location",
        # type
        "category",
        # date
        "starttime",
        "endtime",
        # valid
        "metadata_valid",
        "data_valid",
    ),
    Index(
        "index_category_time",
        # type
        "category",
        # date
        "starttime",
        "endtime",
    ),
)


async def get_metadata(
    *,  # make all params keyword
    network: str,
    station: str,
    channel: str = None,
    location: str = None,
    category: MetadataCategory = None,
    starttime: UTCDateTime = None,
    endtime: UTCDateTime = None,
    data_valid: bool = None,
    metadata_valid: bool = None,
):
    query = (
        metadata.select()
        .where(metadata.c.network.like(network or "%"))
        .where(metadata.c.station.like(station or "%"))
        .where(metadata.c.channel.like(channel or "%"))
        .where(metadata.c.location.like(location or "%"))
    )
    if starttime:
        query = query.where(
            or_(metadata.c.endtime == None, metadata.c.endtime > starttime.datetime)
        )
    if endtime:
        query = query.where(
            or_(metadata.c.starttime == None, metadata.c.starttime < endtime.datetime)
        )
    if data_valid is not None:
        query = query.where(metadata.c.data_valid == data_valid)
    if metadata_valid is not None:
        query = query.where(metadata.c.metadata_valid == metadata_valid)
