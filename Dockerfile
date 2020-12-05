ARG FROM_IMAGE=usgs/obspy:3.8

FROM ${FROM_IMAGE}
LABEL maintainer="Jeremy Fee <jmfee@usgs.gov>"

ARG GIT_BRANCH_NAME=none
ARG GIT_COMMIT_SHA=none
ARG WEBSERVICE="false"

# set environment variables
ENV GIT_BRANCH_NAME=${GIT_BRANCH_NAME} \
    GIT_COMMIT_SHA=${GIT_COMMIT_SHA} \
    WEBSERVICE=${WEBSERVICE}


RUN useradd \
    -c 'Docker image user' \
    -m \
    -r \
    -s /sbin/nologin \
    geomag_user \
    && mkdir -p /data \
    && chown -R geomag_user:geomag_user /data

USER geomag_user

# install dependencies via pipenv
WORKDIR /data
COPY Pipfile /data/
RUN pipenv --site-packages install --dev --skip-lock

# copy library (ignores set in .dockerignore)
COPY . /geomag-algorithms

# entrypoint needs double quotes
ENTRYPOINT [ "/geomag-algorithms/docker-entrypoint.sh" ]
EXPOSE 8000
