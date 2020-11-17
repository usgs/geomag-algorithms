from datetime import timezone
import json
from typing import Dict

from obspy import UTCDateTime
from pydantic import BaseModel, validator

from .. import pydantic_utcdatetime
from .MetadataCategory import MetadataCategory


class Metadata(BaseModel):
    """
    This class is used for Data flagging and other Metadata.

    Flag example:
    ```
    automatic_flag = Metadata(
        created_by = 'algorithm/version',
        start_time = UTCDateTime('2020-01-02T00:17:00.1Z'),
        end_time = UTCDateTime('2020-01-02T00:17:00.1Z'),
        network = 'NT',
        station = 'BOU',
        channel = 'BEU',
        category = MetadataCategory.FLAG,
        comment = "spike detected",
        priority = 1,
        data_valid = False)
    ```

    Adjusted Matrix example:
    ```
    adjusted_matrix = Metadata(
        created_by = 'algorithm/version',
        start_time = UTCDateTime('2020-01-02T00:17:00Z'),
        end_time = None,
        network = 'NT',
        station = 'BOU',
        category = MetadataCategory.ADJUSTED_MATRIX,
        comment = 'automatic adjusted matrix',
        priority = 1,
        value = {
            'parameters': {'x': 1, 'y': 2, 'z': 3}
            'matrix': [ ... ]
        }
    )
    ```
    """

    # database id
    id: int = None
    # author
    created_by: str = None
    created_time: UTCDateTime = None
    # reviewer
    reviewed_by: str = None
    reviewed_time: UTCDateTime = None
    # time range
    starttime: UTCDateTime = None
    endtime: UTCDateTime = None
    # what data metadata references, null for wildcard
    network: str = None
    station: str = None
    channel: str = None
    location: str = None
    # category (flag, matrix, etc)
    category: MetadataCategory = None
    # higher priority overrides lower priority
    priority: int = 1
    # whether data is valid (primarily for flags)
    data_valid: bool = True
    # whether metadata is valid (based on review)
    metadata_valid: bool = True
    # metadata json blob
    metadata: Dict = None
    # general comment
    comment: str = None
    # review specific comment
    review_comment: str = None

    def datetime_dict(self, **kwargs):
        values = self.dict(**kwargs)
        for key in ["created_time", "reviewed_time", "starttime", "endtime"]:
            if key in values and values[key] is not None:
                values[key] = values[key].datetime.replace(tzinfo=timezone.utc)
        return values

    @validator("created_time")
    def set_default_created_time(cls, created_time: UTCDateTime = None) -> UTCDateTime:
        return created_time or UTCDateTime()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
