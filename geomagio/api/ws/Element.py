from typing import Optional
from pydantic import BaseModel


class Element(BaseModel):
    id: str
    abbreviation: Optional[str]
    name: str
    units: str


ELEMENTS = [
    Element(id="H", name="North Component", units="nT"),
    Element(id="E", name="East Component", units="nT"),
    Element(id="X", name="Geographic North Magnitude", units="nT"),
    Element(id="Y", name="Geographic East Magnitude", units="nT"),
    Element(id="D", name="Declination (deci-arcminute)", units="dam"),
    Element(id="Z", name="Vertical Component", units="nT"),
    Element(id="F", name="Total Field Magnitude", units="nT"),
    Element(id="G", abbreviation="ΔF", name="Delta F", units="∆nT"),
    Element(id="DIST", name="Disturbance", units="nT"),
    Element(id="E-E", name="E=Field East", units="mV/km"),
    Element(id="E-N", name="E-Field North", units="mV/km"),
    Element(id="SQ", name="Solar Quiet", units="nT"),
    Element(id="SV", name="Solar Variation", units="nT"),
    Element(
        id="UK1", abbreviation="T-Electric", name="Electronics Temperature", units="°C",
    ),
    Element(
        id="UK2",
        abbreviation="T-Total Field",
        name="Total Field Temperature",
        units="°C",
    ),
    Element(
        id="UK3", abbreviation="T-Fluxgate", name="Fluxgate Temperature", units="°C"
    ),
    Element(id="UK4", abbreviation="T-Outside", name="Outside Temperature", units="°C"),
    Element(id="DDT", abbreviation="DbDt", name="Time Derivative", units="1/s"),
]

ELEMENT_INDEX = {e.id: e for e in ELEMENTS}
