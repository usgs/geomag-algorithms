class Element(BaseModel):
    id: str
    abbreviation: str
    name: str
    units: str


elements = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "H",
            "properties": {"name": "Observatory North Component", "units": "nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "E",
            "properties": {"name": "Observatory East Component", "units": "nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "D",
            "properties": {"name": "Declination (deci-arcminute)", "units": "dam"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "Z",
            "properties": {"name": "Observatory Vertical Component", "units": "nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "F",
            "properties": {"name": "Total Field Magnitude", "units": "nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "G",
            "properties": {"abbreviation": "ΔF", "name": "Delta F", "units": "∆nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "X",
            "properties": {"name": "Geographic North Magnitude", "units": "nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "Y",
            "properties": {"name": "Geographic East Magnitude", "units": "nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "MDT",
            "properties": {
                "abbreviation": "Dist",
                "name": "Disturbance",
                "units": "nT",
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "MSQ",
            "properties": {"abbreviation": "SQ", "name": "Solar Quiet", "units": "nT"},
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "MSV",
            "properties": {
                "abbreviation": "SV",
                "name": "Solar Variation",
                "units": "nT",
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "E-N",
            "properties": {
                "abbreviation": "E-N",
                "name": "E-Field North",
                "units": "mV/km",
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "E-E",
            "properties": {
                "abbreviation": "E-E",
                "name": "E-Field East",
                "units": "mV/km",
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "UK1",
            "properties": {
                "abbreviation": "T-Electric",
                "name": "Electronics Temperature",
                "units": "°C",
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "UK3",
            "properties": {
                "abbreviation": "T-Fluxgate",
                "name": "Fluxgate Temperature",
                "units": "°C",
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "UK2",
            "properties": {
                "abbreviation": "T-Total Field",
                "name": "Total Field Temperature",
                "units": "°C",
            },
            "geometry": None,
        },
        {
            "type": "Feature",
            "id": "UK4",
            "properties": {
                "abbreviation": "T-Outside",
                "name": "Outside Temperature",
                "units": "°C",
            },
            "geometry": None,
        },
    ],
}
