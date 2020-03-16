# Installation

> - [Develop](./develop.md) describes how to install locally.
> - [Docker](./install_docker.md) describes container usage.

## Requirements:

- Python 3.6 or newer
- ObsPy 1.2.1 or newer

## Procedure:

1.  Install Python and dependencies

    - Option 1: Anaconda/Miniconda (https://conda.io/miniconda.html):

          conda create --name=geomagenv --channel conda-forge python=3 obspy pycurl
          source activate geomagenv

    - Option 2: Pip

      > `pyenv` can install specific/multiple versions of python
      >
      > - https://github.com/pyenv/pyenv
      > - https://github.com/pyenv-win/pyenv-win

          # create virtual environment (optional)
          python -m venv path/to/geomagenv
          source path/to/geomagenv/bin/activate

          # install dependencies
          pip install numpy
          pip install obspy

2.  Install **geomagio**

        pip install git+https://github.com/usgs/geomag-algorithms.git

3.  Use **geomagio**

    - Use the main script, `geomag.py -h`
    - In python scripts, `import geomagio`
    - Interactively with Jupyter notebooks ( http://jupyter.org/install.html )
