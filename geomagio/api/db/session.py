import datetime
import json
from typing import Dict, Optional


import orm
from .common import database, sqlalchemy_metadata


class Session(orm.Model):
    """Model for database sessions.
    """

    __tablename__ = "session"
    __database__ = database
    __metadata__ = sqlalchemy_metadata

    id = orm.Integer(primary_key=True)
    session_id = orm.String(index=True, max_length=100)
    data = orm.Text()
    updated = orm.DateTime(index=True)


async def delete_session(session_id: str):
    try:
        session = await Session.objects.get(session_id=session_id)
        await session.delete()
    except orm.exceptions.NoMatch:
        return {}


async def get_session(session_id: str) -> str:
    try:
        session = await Session.objects.get(session_id=session_id)
        return session.data
    except orm.exceptions.NoMatch:
        return {}


async def remove_expired_sessions(max_age: datetime.timedelta):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    await Session.objects.delete(updated__lt=(now - max_age))


async def save_session(session_id: str, data: str):
    updated = datetime.datetime.now(tz=datetime.timezone.utc)
    try:
        session = await Session.objects.get(session_id=session_id)
        await session.update(data=data, updated=updated)
    except orm.exceptions.NoMatch:
        await Session.objects.create(session_id=session_id, data=data, updated=updated)
