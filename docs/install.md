Installation
============

Using Anaconda is recommended ( https://conda.io/miniconda.html ).


1) Install Anaconda/Miniconda

2) Create a virtual environment

        conda config --add channels conda-forge
        conda create --name geomagenv obspy pycurl flake8 nose
        source activate geomagenv

3) Install **geomagio**

        pip install git+https://github.com/usgs/geomag-algorithms.git

4) Use **geomagio**

  - Use the main script, `geomag.py -h`
  - In python scripts, `import geomagio`
  - Install the Jupyter notebook server ( http://jupyter.org/install.html )
