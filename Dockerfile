ARG FROM_IMAGE=usgs/centos:8

FROM ${FROM_IMAGE}
LABEL maintainer="Jeremy Fee <jmfee@usgs.gov>"

# set environment variables
ENV PATH /conda/bin:$PATH \
    LC_ALL='en_US.UTF-8' \
    LANG='en_US.UTF-8' \
    PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

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
    && pip install pipenv \
    && yum install -y which && yum clean all

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
COPY Pipfile Pipfile.lock /data/
RUN pipenv install  --site-packages

# copy library (ignores set in .dockerignore)
COPY . /geomag-algorithms

EXPOSE 8000

# entrypoint needs double quotes
ENTRYPOINT [ "/geomag-algorithms/docker-entrypoint.sh" ]
