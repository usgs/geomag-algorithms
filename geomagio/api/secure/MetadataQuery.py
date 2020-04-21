from datetime import timezone

from obspy import UTCDateTime
from pydantic import BaseModel, validator

from ...metadata import MetadataCategory
from ... import pydantic_utcdatetime


class MetadataQuery(BaseModel):
    id: int = None
    category: MetadataCategory = None
    starttime: UTCDateTime = None
    endtime: UTCDateTime = None
    network: str = None
    station: str = None
    channel: str = None
    location: str = None
    data_valid: bool = None
    metadata_valid: bool = True

    def datetime_dict(self, **kwargs):
        values = self.dict(**kwargs)
        for key in ["starttime", "endtime"]:
            if key in values and values[key] is not None:
                values[key] = values[key].datetime.replace(tzinfo=timezone.utc)
        return values

    @validator("starttime")
    def set_default_starttime(cls, starttime: UTCDateTime = None) -> UTCDateTime:
        return starttime or UTCDateTime() - 30 * 86400
