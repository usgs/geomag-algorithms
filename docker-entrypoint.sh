#! /bin/bash

# run jupyter in the background, and forward SIGTERM manually.
# "exec" seems like a much simpler solution for this,
# however, jupyter kernels die noisy deaths when using exec.

# _term () {
#  echo 'Caught SIGTERM'
#  kill -TERM "$child"
#}
#trap _term SIGTERM

# add geomagio to notebook path
export PYTHONPATH=/geomag-algorithms

# run jupyter notebook server
exec jupyter notebook \
    --ip='*' \
    --notebook-dir=/home/geomag_user/notebooks \
    --no-browser \
    --port=8000

#child=$!
#wait "$child"
