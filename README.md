Geomag Algorithms
=================

Geomag algorithms includes tools to fetch, process, and output geomag data.

[Documentation](./docs/README.md)


Install
-------

We recommend using [virtual environments][].

__Windows__: begin with the Windows dependencies in the
[Dependency install](readme_dependency_install.md#windows).

__Mac/Linux__: begin with required dependencies in the
[Dependency install](readme_dependency_install.md#mac).

1. Install geomagio

        pip install git+https://github.com/usgs/geomag-algorithms.git

1. Use geomagio

    - Use the main script, `geomag.py -h`.
    - In python scripts, `import geomagio`.

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
