#! /bin/bash

# Environment variable to determine whether to start webservice
export WEBSERVICE=${WEBSERVICE:-false}

# add geomagio to notebook path
export PYTHONPATH=/geomag-algorithms


if [ $WEBSERVICE = 'false' ]; then
  # run jupyter notebook server
  exec jupyter notebook \
      --ip='*' \
      --notebook-dir=/data \
      --no-browser \
      --port=8000
else
  # run gunicorn server for web service
  exec pipenv run gunicorn \
      --access-logfile - \
      --bind 0.0.0.0:8000 \
      --threads 2 \
      --workers 2 \
      --worker-class uvicorn.workers.UvicornWorker \
      --worker-tmp-dir /dev/shm \
      geomagio.api:app
fi
