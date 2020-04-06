"""Configure pydantic to allow UTCDateTime attributes on models.
"""
from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple, TypeVar, Union

from obspy import UTCDateTime
from pydantic.errors import PydanticValueError
import pydantic.json
import pydantic.schema
import pydantic.validators


# placeholder type for register_custom_pydantic_type method
CustomType = TypeVar("CustomType")


def register_custom_pydantic_type(
    custom_type: CustomType,
    encoder: Callable[[CustomType], Any],
    json_schema: Dict,
    parsers: List[Callable[[Any], CustomType]],
):
    try:
        if custom_type.__custom_pydantic_type__:
            # already registered
            return
    except AttributeError:
        # not registered yet
        pass
    # add encoder
    pydantic.json.ENCODERS_BY_TYPE[custom_type] = encoder
    # add openapi mapping
    pydantic.schema.field_class_to_schema += ((custom_type, json_schema),)
    # add validator
    pydantic.validators._VALIDATORS.append((custom_type, parsers))
    # mark as installed
    custom_type.__custom_pydantic_type__ = True


class UTCDateTimeError(PydanticValueError):
    msg_template = "invalid date-time format"


def format_utcdatetime(o: UTCDateTime) -> str:
    return o.isoformat()


def parse_utcdatetime(
    value: Union[datetime, float, int, str, UTCDateTime]
) -> UTCDateTime:
    try:
        return UTCDateTime(value)
    except:
        raise UTCDateTimeError()


register_custom_pydantic_type(
    UTCDateTime,
    encoder=format_utcdatetime,
    json_schema={"type": "string", "format": "date-time"},
    parsers=[parse_utcdatetime],
)
