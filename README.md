Geomag Algorithms
=================

Geomag algorithms includes tools to fetch, process, and output geomag data.


Install
-------

We recommend using [virtual environments][]


1. Install `python` (2.7.X)

    - On OS X, we recommend using Homebrew ( http://brew.sh/ )

2. Install numpy, obspy requires this be installed separately.

        pip install numpy

3. Install geomagio

        pip install git+https://github.com/usgs/geomag-algorithms.git

4. Use geomagio

    - Use the xyz main script, `xyz.py -h`.
    - In python scripts, `import geomagio` or `import geomagio.iaga2002`.

[virtual environments]: http://docs.python-guide.org/en/latest/dev/virtualenvs/


Developing
----------

1. Use npm to install `grunt-cli`

        npm install -g grunt-cli

2. Install `numpy`, `scipy`, `obspy`, and `flake8`

3. Clone this project (or fork and clone your fork)

        git clone https://github.com/usgs/geomag-algorithms.git

4. From root directory of project, install npm dependencies

        npm install

5. Run grunt to run unit tests, and watch for changes to python files

        grunt


Coding Standards
----------------

This project adheres to PEP8 standards in most cases:
    https://www.python.org/dev/peps/pep-0008

### PEP8 Exceptions

- Hanging/Visual indents (E126, E127, E128, E131)

    - line continuations should use two indentations (8 spaces).
    - do not use visual indents.

[Dependency install details for Windows and Mac](readme_dependency_install.md)
