from typing import Dict

from fastapi import APIRouter

from .Observatory import OBSERVATORIES, OBSERVATORY_INDEX


router = APIRouter()


@router.get("/observatories/")
def get_observatories() -> Dict:
    return {
        "type": "FeatureCollection",
        "features": [o.to_json() for o in OBSERVATORIES],
    }


@router.get("/observatories/{id}")
async def get_observatory_by_id(id: str) -> Dict:
    return OBSERVATORY_INDEX[id].to_json()
