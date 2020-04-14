from datetime import datetime, timedelta, timezone
import json
from typing import Dict, Optional

import sqlalchemy
import sqlalchemy_utc

from .common import database, sqlalchemy_metadata


session = sqlalchemy.Table(
    "session",
    sqlalchemy_metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("session_id", sqlalchemy.String(length=100), index=True),
    sqlalchemy.Column("data", sqlalchemy.Text),
    sqlalchemy.Column("updated", sqlalchemy_utc.UtcDateTime, index=True),
)


async def delete_session(session_id: str) -> None:
    query = session.delete().where(session.c.session_id == session_id)
    await database.execute(query)


async def get_session(session_id: str) -> str:
    query = session.select().where(session.c.session_id == session_id)
    row = await database.fetch_one(query)
    return row.data


async def remove_expired_sessions(max_age: timedelta) -> None:
    threshold = datetime.now(tz=timezone.utc) - max_age
    query = session.delete().where(session.c.updated < threshold)
    await database.execute(query)


async def save_session(session_id: str, data: str) -> None:
    updated = datetime.now(tz=timezone.utc)
    # try update first
    query = (
        session.update()
        .where(session.c.session_id == session_id)
        .values(data=data, updated=updated)
    )
    count = await database.execute(query)
    if count == 0:
        # no matching session, insert
        query = session.insert().values(
            session_id=session_id, data=data, updated=updated
        )
        await database.execute(query)
