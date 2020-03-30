import enum
from typing import Any, List, Union

from pydantic import BaseModel, root_validator, validator

REQUEST_LIMIT = 345600
VALID_DATA_TYPES = ["variation", "adjusted", "quasi-definitive", "definitive"]
VALID_ELEMENTS = [
    "D",
    "DIST",
    "DST",
    "E",
    "E-E",
    "E-N",
    "F",
    "G",
    "H",
    "SQ",
    "SV",
    "UK1",
    "UK2",
    "UK3",
    "UK4",
    "X",
    "Y",
    "Z",
]
VALID_OBSERVATORIES = [
    "BDT",
    "BOU",
    "BRT",
    "BRW",
    "BSL",
    "CMO",
    "CMT",
    "DED",
    "DHT",
    "FDT",
    "FRD",
    "FRN",
    "GUA",
    "HON",
    "NEW",
    "SHU",
    "SIT",
    "SJG",
    "SJT",
    "TST",
    "TUC",
    "USGS",
]


class DataType(str, enum.Enum):
    VARIATION = "variation"
    ADJUSTED = "adjusted"
    QUASI_DEFINITIVE = "quasi-definitive"
    DEFINITIVE = "definitive"


class OutputFormat(str, enum.Enum):
    IAGA2002 = "iaga2002"
    JSON = "json"


class SamplingPeriod(float, enum.Enum):
    TEN_HERTZ = 0.1
    SECOND = 1.0
    MINUTE = 60
    HOUR = 3600
    DAY = 86400


class DataApiQuery(BaseModel):
    id: str
    starttime: Any
    endtime: Any
    elements: List[str]
    sampling_period: SamplingPeriod
    data_type: Union[DataType, str]
    format: OutputFormat

    @validator("data_type")
    def validate_data_type(cls, data_type):
        if len(data_type) != 2 and data_type not in DataType:
            raise ValueError(
                f"Bad data type value '{data_type}'. Valid values are: {', '.join(VALID_DATA_TYPES)}"
            )
        return data_type

    @validator("elements")
    def validate_elements(cls, elements):
        for element in elements:
            if element not in VALID_ELEMENTS and len(element) != 3:
                raise ValueError(
                    f"Bad element '{element}'."
                    f"Valid values are: {', '.join(VALID_ELEMENTS)}."
                )
        return elements

    @validator("id")
    def validate_id(cls, id):
        if id not in VALID_OBSERVATORIES:
            raise ValueError(
                f"Bad observatory id '{id}'."
                f" Valid values are: {', '.join(VALID_OBSERVATORIES)}."
            )
        return id

    @root_validator
    def validate_times(cls, values):
        starttime, endtime, elements, format, sampling_period = (
            values.get("starttime"),
            values.get("endtime"),
            values.get("elements"),
            values.get("format"),
            values.get("sampling_period"),
        )
        if starttime > endtime:
            raise ValueError("Starttime must be before endtime.")

        if len(elements) > 4 and format == "iaga2002":
            raise ValueError("No more than four elements allowed for iaga2002 format.")

        samples = int(len(elements) * (endtime - starttime) / sampling_period)
        # check data volume
        if samples > REQUEST_LIMIT:
            raise ValueError(f"Query exceeds request limit ({samples} > 345600)")

        return values
