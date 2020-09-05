#! /bin/bash -x

PYTHON_VERSION=${PYTHON_VERSION:-"3.8"}


if [ -f "/etc/profile.d/conda.sh" ]; then
  # Add conda to path
  source /etc/profile.d/conda.sh
fi

# Install Project Dependencies
conda config --add channels conda-forge
conda install python=${PYTHON_VERSION} obspy pycurl
pip install pipenv
pipenv --site-packages install --dev --pre --skip-lock

# Run Code Checks
pipenv run black --check .
pipenv run pytest --cov-report xml:cov.xml --cov=geomagio
