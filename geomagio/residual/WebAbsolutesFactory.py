import json
import urllib
from typing import Dict, IO, List, Mapping

from obspy.core import UTCDateTime

from .Absolute import Absolute
from .Measurement import Measurement
from .MeasurementType import MeasurementType
from .Reading import Reading


class WebAbsolutesFactory(object):
    """Read absolutes from web absolutes service."""

    def __init__(
        self, url: str = "https://geomag.usgs.gov/baselines/observation.json.php"
    ):
        self.url = url

    def get_readings(
        self,
        observatory: str,
        starttime: UTCDateTime,
        endtime: UTCDateTime,
        include_measurements: bool = True,
    ) -> List[Reading]:
        """Get readings from the Web Absolutes Service."""
        args = urllib.parse.urlencode(
            {
                "observatory": observatory,
                "starttime": starttime.isoformat(),
                "endtime": endtime.isoformat(),
                "includemeasurements": include_measurements and "true" or "false",
            }
        )
        with urllib.request.urlopen(f"{self.url}?{args}") as data:
            return self.parse_json(data)

    def parse_json(self, jsonstr: IO[str]) -> List[Reading]:
        """Parse readings from the web absolutes JSON format."""
        readings = []
        response = json.load(jsonstr)
        for data in response["data"]:
            metadata = self._parse_metadata(data)
            readings.extend(
                [self._parse_reading(metadata, r) for r in data["readings"]]
            )
        return readings

    def _parse_absolute(self, element: str, data: Mapping) -> Absolute:
        return Absolute(
            element=element,
            absolute=data["absolute"],
            baseline=data["baseline"],
            starttime=data["start"] and UTCDateTime(data["start"]) or None,
            endtime=data["end"] and UTCDateTime(data["end"]) or None,
            shift="shift" in data and data["shift"] or 0,
            valid=data["valid"],
        )

    def _parse_measurement(self, data: Mapping) -> Measurement:
        return Measurement(
            measurement_type=MeasurementType(data["type"]),
            angle=data["angle"],
            residual=0,
            time=data["time"] and UTCDateTime(data["time"]) or None,
            h=data["h"],
            e=data["e"],
            z=data["z"],
            f=data["f"],
        )

    def _parse_metadata(self, data: Mapping) -> Dict:
        return {
            "time": data["time"],
            "reviewed": data["reviewed"],
            "electronics": data["electronics"]["serial"],
            "theodolite": data["theodolite"]["serial"],
            "mark_name": data["mark"]["name"],
            "mark_azimuth": data["mark"]["azimuth"],
            "pier_name": data["pier"]["name"],
            "pier_correction": data["pier"]["correction"],
            "observer": data["observer"],
            "reviewer": data["reviewer"],
        }

    def _parse_reading(self, metadata: Mapping, data: Mapping) -> Reading:
        """Parse absolutes and measurements from Reading json."""
        absolutes = [
            self._parse_absolute(element, data[element])
            for element in ["D", "H", "Z"]
            if element in data
        ]
        measurements = (
            [self._parse_measurement(m) for m in data["measurements"]]
            if "measurements" in data
            else []
        )
        return Reading(
            absolutes=absolutes,
            azimuth=("mark_azimuth" in metadata and metadata["mark_azimuth"] or 0),
            hemisphere=1,
            measurements=measurements,
            metadata=metadata,
            pier_correction=(
                "pier_correction" in metadata and metadata["pier_correction"] or 0
            ),
        )
