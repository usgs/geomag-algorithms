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
    created_after: UTCDateTime = None
    created_before: UTCDateTime = None
    network: str = None
    station: str = None
    channel: str = None
    location: str = None
    data_valid: bool = None
    metadata_valid: bool = True

    def datetime_dict(self, **kwargs):
        values = self.dict(**kwargs)
        for key in ["starttime", "endtime", "created_after", "created_before"]:
            if key in values and values[key] is not None:
                values[key] = values[key].datetime.replace(tzinfo=timezone.utc)
        return values
