from typing import Dict

from fastapi import APIRouter

from .Element import ELEMENTS


router = APIRouter()


@router.get("/elements/")
def get_elements() -> Dict:
    features = []
    for e in ELEMENTS:
        feature = {
            "type": "Feature",
            "id": e.id,
            "properties": {
                "name": e.name,
                "units": e.units,
            },
            "geometry": None,
        }
        if e.abbreviation:
            feature["properties"]["abbreviation"] = e.abbreviation
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}
