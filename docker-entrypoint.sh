#! /bin/bash

# add geomagio to notebook path
export PYTHONPATH=/geomag-algorithms

# run jupyter notebook server
exec jupyter notebook \
    --ip='*' \
    --notebook-dir=/data \
    --no-browser \
    --port=8000
