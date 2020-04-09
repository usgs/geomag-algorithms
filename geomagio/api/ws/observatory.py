from pydantic import BaseModel, validator
from typing import Dict


class Observatory(BaseModel):
    id: str
    elevation: int
    latitude: float
    longitude: float
    name: str
    agency: str
    agency_name: str
    declination_base: int
    sensor_orientation: str

    @validator("agency_name", always=true)
    def validate_agency_name(cls, agency_name: str, values: Dict) -> str:
        agency = values.get("agency")
        if not agency_name:
            if agency == "USGS":
                agency_name = "United States Geological Survey (USGS)"
            if agency == "GSC":
                agency_name = "Geological Survey of Canada (GSC)"
            if agency == "BGS":
                agency_name = "British Geological Survey (BGS)"
            if agency == "SANSA":
                agency_name = "South African National Space Agency (SANSA)"
            if agency == "JMA":
                agency_name = "Japan Meteorological Agency (JMA)"
        return agency_name

    @validator("sensor_orientation", always=true)
    def validate_sensor_orientation(cls, sensor_orientation: str, values: Dict) -> str:
        agency = values.get("agency")

        if not sensor_orientation:
            if agency == "GSC":
                sensor_orientation = "XYZF"
            else:
                sensor_orientation = "HDZF"
            return sensor_orientation


OBSERVATORIES = [
    Observatory(
        id="BDT",
        elevation=1682,
        latitude=40.137,
        longitude=254.763,
        name="Boulder Test",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=5527,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="BOU",
        elevation=1682,
        latitude=40.137,
        longitude=254.763,
        name="Boulder",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=5527,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="TST",
        elevation=1682,
        latitude=40.137,
        longitude=254.763,
        name="Boulder Test (ObsRIO)",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=5527,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="BRW",
        elevation=10,
        latitude=203.378,
        longitude=71.322,
        name="Barrow",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=10589,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="BRT",
        elevation=10,
        latitude=203.378,
        longitude=71.322,
        name="Barrow Test (ObsRIO)",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=10589,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="BSL",
        elevation=8,
        latitude=30.35,
        longitude=270.365,
        name="Stennis Space Center",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=215772,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="CMO",
        elevation=197,
        latitude=64.874,
        longitude=212.14,
        name="College",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=12151,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="CMT",
        elevation=197,
        latitude=64.874,
        longitude=212.14,
        name="College (ObsRIO)",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=12151,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="DED",
        elevation=10,
        latitude=70.355,
        longitude=211.207,
        name="Deadhorse",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=10755,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="DHT",
        elevation=10,
        latitude=70.355,
        longitude=211.207,
        name="Deadhorse Test (ObsRIO)",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=10755,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="FRD",
        elevation=69,
        latitude=38.205,
        longitude=282.627,
        name="Fredericksburg",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=209690,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="FRT",
        elevation=69,
        latitude=38.205,
        longitude=282.627,
        name="Fredericksburg Test",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=209690,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="FRN",
        elevation=331,
        latitude=37.091,
        longitude=240.282,
        name="Fresno",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=8097,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="GUA",
        elevation=140,
        latitude=13.588,
        longitude=144.867,
        name="Guam",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=764,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="HON",
        elevation=4,
        latitude=21.316,
        longitude=202.0,
        name="Honolulu",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=5982,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="NEW",
        elevation=770,
        latitude=48.265,
        longitude=242.878,
        name="Newport",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=9547,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="SHU",
        elevation=80,
        latitude=55.348,
        longitude=199.538,
        name="Shumagin",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=7386,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="SIT",
        elevation=24,
        latitude=57.058,
        longitude=224.675,
        name="Sitka",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=12349,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="SJG",
        elevation=424,
        latitude=18.113,
        longitude=293.849,
        name="San Juan",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=208439,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="SJT",
        elevation=424,
        latitude=18.113,
        longitude=293.849,
        name="San Juan Test",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=208439,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="TUC",
        elevation=946,
        latitude=32.174,
        longitude=249.267,
        name="Tucson",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=5863,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="USGS",
        elevation=1682,
        latitude=40.137,
        longitude=254.764,
        name="USGS",
        agency="USGS",
        agency_name="United States Geological Survey (USGS)",
        declination_base=0,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="BLC",
        elevation=0,
        latitude=64.3,
        longitude=264.0,
        name="Baker Lake",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="BRD",
        elevation=0,
        latitude=49.6,
        longitude=262.9,
        name="Brandon",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="CBB",
        elevation=0,
        latitude=69.2,
        longitude=255.0,
        name="Cambridge Bay",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="EUA",
        elevation=0,
        latitude=55.3,
        longitude=282.3,
        name="Eureka",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="FCC",
        elevation=0,
        latitude=58.8,
        longitude=265.9,
        name="Fort Churchill",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="IQA",
        elevation=0,
        latitude=63.8,
        longitude=291.5,
        name="Iqaluit",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="MEA",
        elevation=0,
        latitude=54.6,
        longitude=246.7,
        name="Meanook",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="OTT",
        elevation=0,
        latitude=45.4,
        longitude=284.5,
        name="Ottawa",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="RES",
        elevation=0,
        latitude=74.7,
        longitude=265.1,
        name="Resolute Bay",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="SNK",
        elevation=0,
        latitude=62.4,
        longitude=245.5,
        name="Sanikiluaq",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="STJ",
        elevation=0,
        latitude=47.6,
        longitude=307.3,
        name="St Johns",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="VIC",
        elevation=0,
        latitude=48.6,
        longitude=236.6,
        name="Victoria",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="YKC",
        elevation=0,
        latitude=62.4,
        longitude=245.5,
        name="Yellowknife",
        agency="GSC",
        agency_name="Geological Survey of Canada (GSC)",
        declination_base=0,
        sensor_orientation="XYZF",
    ),
    Observatory(
        id="HAD",
        elevation=0,
        latitude=51.0,
        longitude=355.5,
        name="Hartland",
        agency="BGS",
        agency_name="British Geological Survey (BGS)",
        declination_base=0,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="HER",
        elevation=0,
        latitude=-34.4,
        longitude=19.2,
        name="Hermanus",
        agency="SANSA",
        agency_name="South African National Space Agency (SANSA)",
        declination_base=0,
        sensor_orientation="HDZF",
    ),
    Observatory(
        id="KAK",
        elevation=36,
        latitude=53.77,
        longitude=140.18,
        name="Kakioka",
        agency="JMA",
        agency_name="Japan Meteorological Agency (JMA)",
        declination_base=0,
        sensor_orientation="HDZF",
    ),
]

OBSERVATORY_INDEX = {o.id: o for o in OBSERVATORIES}
