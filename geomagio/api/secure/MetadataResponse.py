from typing import Dict, List

from pydantic import BaseModel

from ...metadata import Metadata
from .MetadataQuery import MetadataQuery


class MetadataResponse(BaseModel):
    query: MetadataQuery
    results: List[Metadata]
