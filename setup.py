from distutils.core import setup

setup(
    name='geomag-algorithms',
    version='0.0.0',
    desription='USGS Geomag IO Library',
    url='https://github.com/usgs/geomag-algorithms',
    packages=[
        'geomagio',
        'geomagio.iaga2002'
        'geomagio.edge'
    ],
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'obspy'
    ],
    scripts=[
        'bin/geomag.py'
    ]
)
