from __future__ import unicode_literals

"""Dictionary of observatory codes and ness block byte orders"""
OBSERVATORIES = {
    # USGS
    'BOU': {
        'orient': 'HEZF',
        'platform': '75C2D538',
        'swap_hdr': False,
        'swap_data': True
    },
    'BRW': {
        'orient': 'HEZF',
        'platform': '75C172CE',
        'swap_hdr': False,
        'swap_data': True
    },
    'BSL': {
        'orient': 'HEZF',
        'platform': '75C236CA',
        'swap_hdr': False,
        'swap_data': True
    },
    'CMO': {
        'orient': 'HEZF',
        'platform': '75C06342',
        'swap_hdr': False,
        'swap_data': True
    },
    'DED': {
        'orient': 'HEZF',
        'platform': '75C301AA',
        'swap_hdr': False,
        'swap_data': True
    },
    'FRD': {
        'orient': 'HEZF',
        'platform': '75C21026',
        'swap_hdr': False,
        'swap_data': True
    },
    'FRN': {
        'orient': 'HEZF',
        'platform': '75C2F3D4',
        'swap_hdr': False,
        'swap_data': True
    },
    'GUA': {
        'orient': 'HEZF',
        'platform': '75C33430',
        'swap_hdr': False,
        'swap_data': True
    },
    'HON': {
        'orient': 'HEZF',
        'platform': '75C161B8',
        'swap_hdr': False,
        'swap_data': True
    },
    'NEW': {
        'orient': 'HEZF',
        'platform': '75C2E0A2',
        'swap_hdr': False,
        'swap_data': True
    },
    'SHU': {
        'orient': 'HEZF',
        'platform': '75C266B6',
        'swap_hdr': False,
        'swap_data': True
    },
    'SIT': {
        'orient': 'HEZF',
        'platform': '75C28544',
        'swap_hdr': False,
        'swap_data': True
    },
    'SJG': {
        'orient': 'HEZF',
        'platform': '75C0B52A',
        'swap_hdr': False,
        'swap_data': True
    },
    'TUC': {
        'orient': 'HEZF',
        'platform': '75C14754',
        'swap_hdr': False,
        'swap_data': True
    },
    # NRCAN
    'BLC': {
        'orient': 'XYZF',
        'platform': '75C3644C',
        'swap_hdr': True,
        'swap_data': False
    },
    'BRD': {
        'orient': 'XYZF',
        'platform': '75C387BE',
        'swap_hdr': True,
        'swap_data': False
    },
    'CBB': {
        'orient': 'XYZF',
        'platform': '75C351D6',
        'swap_hdr': True,
        'swap_data': False
    },
    'EUA': {
        'orient': 'XYZF',
        'platform': '75C2405A',
        'swap_hdr': True,
        'swap_data': False
    },
    'FCC': {
        'orient': 'XYZF',
        'platform': '75C3773A',
        'swap_hdr': True,
        'swap_data': False
    },
    'IQA': {
        'orient': 'XYZF',
        'platform': '75C0F620',
        'swap_hdr': True,
        'swap_data': False
    },
    'MEA': {
        'orient': 'XYZF',
        'platform': '75C32746',
        'swap_hdr': True,
        'swap_data': False
    },
    'OTT': {
        'orient': 'XYZF',
        'platform': '75C20350',
        'swap_hdr': True,
        'swap_data': False
    },
    'RES': {
        'orient': 'XYZF',
        'platform': '75C1D236',
        'swap_hdr': True,
        'swap_data': False
    },
    'SNK': {
        'orient': 'XYZF',
        'platform': '75C15422',
        'swap_hdr': True,
        'swap_data': False
    },
    'STJ': {
        'orient': 'XYZF',
        'platform': '75C1E7AC',
        'swap_hdr': True,
        'swap_data': False
    },
    'VIC': {
        'orient': 'XYZF',
        'platform': '75C2A3A8',
        'swap_hdr': True,
        'swap_data': False
    },
    'YKC': {
        'orient': 'XYZF',
        'platform': '75C312DC',
        'swap_hdr': True,
        'swap_data': False
    },
    # OTHER
    'KGI': {
        'orient': 'HEZF',
        'platform': '75C394C8',
        'swap_hdr': True,
        'swap_data': False
    }
}

PLATFORMS = {}
for obs in OBSERVATORIES:
    PLATFORMS[OBSERVATORIES[obs]['platform']] = obs
