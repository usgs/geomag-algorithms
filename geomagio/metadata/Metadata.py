from typing import Dict

from obspy import UTCDateTime
from pydantic import BaseModel

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
