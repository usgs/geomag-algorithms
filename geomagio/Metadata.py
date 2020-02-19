"""Simulate metadata service until it is implemented.
"""


def get_instrument(observatory, start_time=None, end_time=None, metadata=None):
    """Get instrument metadata

    Args:
      observatory: observatory code
      start_time: start time to match, or None to match any.
      end_time: end time to match, or None to match any.
      metadata: use custom list, defaults to _INSTRUMENT_METADATA
    Returns:
      list of matching metadata
    """
    metadata = metadata or _INSTRUMENT_METADATA
    return [
        m
        for m in metadata
        if m["station"] == observatory and
            (end_time is None or
                m["start_time"] is None or
                m["start_time"] < end_time) and
            (start_time is None or
                m["end_time"] is None or
                m["end_time"] > start_time)
    ]


"""
To make this list easier to maintain:
 - List NT network stations first, then other networks in alphabetical order
 - Within networks, alphabetize by station, then start_time.
"""
_INSTRUMENT_METADATA = [
    {
        "network": "NT",
        "station": "BDT",
        "start_time": None,
        "end_time": None,
        "instrument": {
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
    },
    {
        "network": "NT",
        "station": "LLO",
        "start_time": None,
        "end_time": None,
        "instrument": {
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
    },
]
