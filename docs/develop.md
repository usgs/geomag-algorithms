Development Dependencies
========================

These instructions only need to be completed if you plan on developing new
code for this project, and may also be used to run a local copy of the code.


Begin Developing
----------------

1. Install `obspy`, `pycurl`, `flake8`, `pytest`, `pytest-cov`, `webtest`.
> Using Anaconda is recommended ( https://conda.io/miniconda.html ).

        conda config --add channels conda-forge
        conda create --name geomagenv obspy pycurl flake8 pytest pytest-cov webtest
        source activate geomagenv

2. Fork this project on Github ( https://guides.github.com/activities/forking/ ).

        https://github.com/{YOUR_GITHUB_ACCOUNT}/geomag-algorithms.git

3. Clone your fork

        git clone https://github.com/{YOUR_GITHUB_ACCOUNT}/geomag-algorithms.git
        cd geomag-algorithms
        git remote add upstream https://github.com/usgs/geomag-algorithms.git

4. Use branches to develop new features and submit pull requests.


Developer Tools
---------------

- **Linting errors**
Check for linting errors using Flake8

        cd geomag-algorithms
        flake8

- **Unit tests**
Run unit tests using PyTest

        cd geomag-algorithms
        pytest

- **Unit test coverage**

        cd geomag-algorithms
        pytest --cov=geomagio

- **Automatically run linting and tests while developing**
(Requires NodeJS)

        cd geomag-algorithms
        npm install
        npm run watch

    There are also "npm run" aliases for individual commands which are listed by running

        npm run


Coding Standards
----------------

This project adheres to PEP8 standards in most cases:
    https://www.python.org/dev/peps/pep-0008

**PEP8 Exceptions**

- Hanging/Visual indents (E122, E126, E127, E128, E131)

    - line continuations should use two indentations (8 spaces).
    - do not use visual indents.
