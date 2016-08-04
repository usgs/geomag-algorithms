FROM debian:jessie

MAINTAINER Jeremy Fee <jmfee@usgs.gov>
LABEL usgs.geomag-algorithms.version=0.2.0


# update os
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        bzip2 \
        ca-certificates \
        curl \
        gcc \
        libcurl4-gnutls-dev \
        libglib2.0-0 \
        libgnutls28-dev \
        libsm6 \
        libxext6 \
        libxrender1 && \
    apt-get clean


ENV PATH /conda/bin:$PATH

# install conda and install obspy
RUN echo 'export PATH=/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    curl https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh \
        -o ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /conda && \
    rm ~/miniconda.sh && \
    conda config --add channels obspy && \
    conda install --yes jupyter obspy && \
    conda clean -i -l -t -y && \
    pip install pycurl


# copy library (ignores set in .dockerignore)
COPY . /geomag-algorithms


RUN pip install /geomag-algorithms && \
    mkdir /notebooks


WORKDIR /geomag-algorithms
EXPOSE 80
CMD /bin/bash -c " \
    exec jupyter notebook \
        --ip='*' \
        --notebook-dir=/notebooks \
        --no-browser \
        --port=80 \
    "
