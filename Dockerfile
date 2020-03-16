ARG FROM_IMAGE=usgs/centos:8

FROM $FROM_IMAGE
LABEL maintainer="Jeremy Fee <jmfee@usgs.gov>"


# install conda
ENV PATH /conda/bin:$PATH
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
    && pip install \
        authlib \
        flask \
        flask-login \
        flask-migrate \
        flask-session \
        flask-sqlalchemy \
        psycopg2-binary


# copy library (ignores set in .dockerignore)
COPY . /geomag-algorithms


RUN useradd \
        -c 'Docker image user' \
        -m \
        -r \
        -s /sbin/nologin \
         geomag_user \
    && mkdir -p /data \
    && chown -R geomag_user:geomag_user /data

USER geomag_user
WORKDIR /data
EXPOSE 8000

# entrypoint needs double quotes
ENTRYPOINT [ "/geomag-algorithms/docker-entrypoint.sh" ]
