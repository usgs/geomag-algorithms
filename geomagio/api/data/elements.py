from pydantic import BaseModel


class Element(BaseModel):
    id: str
    abbreviation: str
    name: str
    units: str


ELEMENTS = [
    Element(id="H", abbreviation="H", name="Observatory North Component", units="nT"),
    Element(id="E", abbreviation="E", name="Observatory East Component", units="nT"),
    Element(id="X", abbreviation="X", name="Geographic North Magnitude", units="nT"),
    Element(id="Y", abbreviation="Y", name="Geographic East Magnitude", units="nT"),
    Element(id="D", abbreviation="D", name="Declination (deci-arcminute)", units="dam"),
    Element(
        id="Z", abbreviation="Z", name="Observatory Vertical Component", units="nT"
    ),
    Element(id="F", abbreviation="F", name="Total Field Magnitude", units="nT"),
    Element(
        id="G", abbreviation="ΔF", name="Observatory Vertical Component", units="∆nT"
    ),
    Element(id="E-E", abbreviation="E-E", name="E=Field East", units="mV/km"),
    Element(id="E-N", abbreviation="E-N", name="E-Field North", units="mV/km"),
    Element(id="MDT", abbreviation="DIST", name="Disturbance", units="nT"),
    Element(id="MSQ", abbreviation="SQ", name="Solar Quiet", units="nT"),
    Element(id="MSV", abbreviation="SV", name="Solar Variation", units="nT"),
    Element(
        id="UK1", abbreviation="T-Electric", name="Electronics Temperature", units="°C"
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
]

ELEMENT_INDEX = {e.id: e for e in ELEMENTS}
