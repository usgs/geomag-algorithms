from typing import Dict

from fastapi import APIRouter

from .Observatory import OBSERVATORIES


router = APIRouter()


@router.get("/observatories")
def get_observatories() -> Dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": o.id,
                "properties": {
                    "name": o.name,
                    "agency": o.agency,
                    "agency_name": o.agency_name,
                    "sensor_orientation": o.sensor_orientation,
                    "sensor_sampling_rate": 0.01,
                    "declination_base": o.declination_base,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [o.longitude, o.latitude, o.elevation],
                },
            }
            for o in OBSERVATORIES
        ],
    }


@router.get("/observatories/{id}")
async def get_observatory_by_id(id: str) -> Dict:
    for o in OBSERVATORIES:
        if o.id == id:
            return {
                "id": o.id,
                "properties": {
                    "name": o.name,
                    "agency": o.agency,
                    "agency_name": o.agency_name,
                    "sensor_orientation": o.sensor_orientation,
                    "sensor_sampling_rate": 0.01,
                    "declination_base": o.declination_base,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [o.longitude, o.latitude, o.elevation],
                },
            }
