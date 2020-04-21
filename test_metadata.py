from obspy import UTCDateTime

from geomagio.api.db import database, metadata_table
from geomagio.api.ws.Observatory import OBSERVATORIES
from geomagio.metadata import Metadata, MetadataCategory


test_metadata = [
    Metadata(
        category=MetadataCategory.INSTRUMENT,
        created_by="test_metadata.py",
        network="NT",
        station="BDT",
        metadata={
            "type": "FGE",
            "channels": {
                # each channel maps to a list of components to calculate nT
                # TODO: calculate these lists based on "FGE" type
                "U": [{"channel": "U_Volt", "offset": 0, "scale": 313.2}],
                "V": [{"channel": "V_Volt", "offset": 0, "scale": 312.3}],
                "W": [{"channel": "W_Volt", "offset": 0, "scale": 312.0}],
            },
            "electronics": {
                "serial": "E0542",
                # these scale values are used to convert voltage
                "x-scale": 313.2,  # V/nT
                "y-scale": 312.3,  # V/nT
                "z-scale": 312.0,  # V/nT
                "temperature-scale": 0.01,  # V/K
            },
            "sensor": {
                "serial": "S0419",
                # these constants combine with instrument setting for offset
                "x-constant": 36958,  # nT/mA
                "y-constant": 36849,  # nT/mA
                "z-constant": 36811,  # nT/mA
            },
        },
    ),
    Metadata(
        category=MetadataCategory.INSTRUMENT,
        created_by="test_metadata.py",
        network="NT",
        station="NEW",
        metadata={
            "type": "Narod",
            "channels": {
                "U": [
                    {"channel": "U_Volt", "offset": 0, "scale": 100},
                    {"channel": "U_Bin", "offset": 0, "scale": 500},
                ],
                "V": [
                    {"channel": "V_Volt", "offset": 0, "scale": 100},
                    {"channel": "V_Bin", "offset": 0, "scale": 500},
                ],
                "W": [
                    {"channel": "W_Volt", "offset": 0, "scale": 100},
                    {"channel": "W_Bin", "offset": 0, "scale": 500},
                ],
            },
        },
    ),
    Metadata(
        category=MetadataCategory.INSTRUMENT,
        created_by="test_metadata.py",
        network="NT",
        station="LLO",
        metadata={
            "type": "Narod",
            "channels": {
                "U": [
                    {"channel": "U_Volt", "offset": 0, "scale": 100},
                    {"channel": "U_Bin", "offset": 0, "scale": 500},
                ],
                "V": [
                    {"channel": "V_Volt", "offset": 0, "scale": 100},
                    {"channel": "V_Bin", "offset": 0, "scale": 500},
                ],
                "W": [
                    {"channel": "W_Volt", "offset": 0, "scale": 100},
                    {"channel": "W_Bin", "offset": 0, "scale": 500},
                ],
            },
        },
    ),
]

# add observatories
for observatory in OBSERVATORIES:
    network = "NT"
    if observatory.agency == "USGS":
        network = "NT"
    # rest alphabetical by agency
    elif observatory.agency == "BGS":
        network = "GB"
    elif observatory.agency == "GSC":
        network = "C2"
    elif observatory.agency == "JMA":
        network = "JP"
    elif observatory.agency == "SANSA":
        network = "AF"
    test_metadata.append(
        Metadata(
            category=MetadataCategory.OBSERVATORY,
            created_by="test_metadata.py",
            network=network,
            station=observatory.id,
            metadata=observatory.dict(),
        )
    )


async def load_test_metadata():
    await database.connect()
    for meta in test_metadata:
        await metadata_table.create_metadata(meta)
    await database.disconnect()


if __name__ == "__main__":
    import asyncio

    asyncio.run(load_test_metadata())
