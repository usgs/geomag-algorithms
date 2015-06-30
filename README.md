Geomag Algorithms
=================

Geomag algorithms includes tools to fetch, process, and output geomag data.

## [First Time Install](readme_dependency_install.md) ##
-----

### [Development Dependencies](readme_develop_install.md) ###
-----

Usage
-----

1. Install geomagio

        pip install git+https://github.com/usgs/geomag-algorithms.git

1. Use geomagio

    - Use the main script, `geomag.py -h`.
    - In python scripts, `import geomagio`.

Supported Algorithms
--------------------

## [XYZ Algorithm](./docs/XYZ.md) ##


[Documentation](./docs/README.md)
-------


Coding Standards
----------------

This project adheres to PEP8 standards in most cases:
    https://www.python.org/dev/peps/pep-0008

### PEP8 Exceptions ###

- Hanging/Visual indents (E126, E127, E128, E131)

    - line continuations should use two indentations (8 spaces).
    - do not use visual indents.

