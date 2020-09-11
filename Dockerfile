ARG FROM_IMAGE=usgs/centos:7

FROM ${FROM_IMAGE} as conda
LABEL maintainer="Jeremy Fee <jmfee@usgs.gov>"

ARG GIT_BRANCH_NAME=none
ARG GIT_COMMIT_SHA=none

# set environment variables
ENV GIT_BRANCH_NAME=${GIT_BRANCH_NAME} \
    GIT_COMMIT_SHA=${GIT_COMMIT_SHA} \
    LANG='en_US.UTF-8' \
    LC_ALL='en_US.UTF-8' \
    PATH=/conda/bin:$PATH \
    PIP_CERT=${SSL_CERT_FILE} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REQUESTS_CA_BUNDLE=${SSL_CERT_FILE}

# install conda
RUN echo 'export PATH=/conda/bin:$PATH' > /etc/profile.d/conda.sh \
    && curl \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    -o ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /conda \
    && rm ~/miniconda.sh

# install dependencies via conda
RUN conda config --set ssl_verify $SSL_CERT_FILE \
    && conda config --add channels conda-forge \
    && conda install --yes jupyter obspy pycurl \
    && conda clean --all -y \
    && export PIP_CERT=$SSL_CERT_FILE \
    && pip install pipenv 'virtualenv!=20.0.22' \
    && yum install -y which \
    && yum clean all


################################################################################
## Development image

# build by running
# docker build -t geomag-algorithms-development --target development .

FROM conda as development

# install dependencies via pipenv
WORKDIR /geomag-algorithms
COPY Pipfile /geomag-algorithms
RUN pipenv --site-packages install --dev --skip-lock

# copy library (ignores set in .dockerignore)
COPY . /geomag-algorithms


################################################################################
## Production image

FROM conda

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
RUN pipenv --site-packages install --skip-lock

# copy library (ignores set in .dockerignore)
COPY . /geomag-algorithms

EXPOSE 8000

# entrypoint needs double quotes
ENTRYPOINT [ "/geomag-algorithms/docker-entrypoint.sh" ]
