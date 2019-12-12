ARG BUILD_IMAGE=usgs/centos:7
ARG FROM_IMAGE=usgs/centos:7
FROM $BUILD_IMAGE AS pycurl-build

# install conda dependencies
RUN yum install -y \
        bzip2 \
        gcc \
        libcurl-devel \
    && yum clean all

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
    && conda install --yes jupyter obspy \
    # build pycurl with SFTP support
    && export PIP_CERT=$SSL_CERT_FILE \
    && export PYCURL_SSL_LIBRARY=nss \
    && pip install pycurl \
    # clean up
    && conda clean --all -y


FROM $FROM_IMAGE
LABEL maintainer="Jeremy Fee <jmfee@usgs.gov>"

# use conda install from build container
ENV PATH /conda/bin:$PATH
COPY --from=pycurl-build /conda /conda
COPY --from=pycurl-build /etc/profile.d/conda.sh /etc/profile.d/conda.sh

# copy library (ignores set in .dockerignore)
COPY . /geomag-algorithms


RUN pip install /geomag-algorithms \
    && useradd \
        -c 'Docker image user' \
        -m \
        -r \
        -s /sbin/nologin \
         geomag_user \
    && mkdir -p /home/geomag_user/notebooks \
    && chown -R geomag_user:geomag_user /home/geomag_user

USER geomag_user
WORKDIR /geomag-algorithms
EXPOSE 8000
# entrypoint needs double quotes
ENTRYPOINT [ "/geomag-algorithms/docker-entrypoint.sh" ]
