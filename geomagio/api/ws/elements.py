from typing import Dict

from fastapi import APIRouter

from .Element import ELEMENTS


router = APIRouter()


@router.get("/elements/")
def get_elements() -> Dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": e.id,
                "properties": {"name": e.name, "units": e.units},
                "geometry": None,
            }
            for e in ELEMENTS
        ],
    }
