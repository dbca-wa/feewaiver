# syntax = docker/dockerfile:1.2

# Prepare the base environment.
FROM ubuntu:22.04 as builder_base_feewaiver

LABEL maintainer="asi@dbca.wa.gov.au"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Australia/Perth \
    PRODUCTION_EMAIL=True \
    SECRET_KEY="ThisisNotRealKey" \
    NODE_MAJOR=16

FROM builder_base_feewaiver as apt_packages_feewaiver

# Use Australian Mirrors
# RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list && \
#    mv /etc/apt/sourcesau.list /etc/apt/sources.list

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
    binutils \
    bzip2 \
    ca-certificates \
    cron \
    curl \
    gcc \
    gdal-bin \
    gpg-agent \
    g++ \
    git \
    gunicorn \
    htop \
    libmagic-dev \
    libpq-dev \
    libproj-dev \
    libreoffice \
    mtr \
    patch \
    postgresql-client \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    software-properties-common \
    ssh \
    tzdata \
    vim \
    wget && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install --no-install-recommends -y python3.9 python3.9-dev python3.9-distutils && \
    ln -s /usr/bin/python3.9 /usr/bin/python && \
    python3.9 -m pip install --upgrade pip && \
    apt-get install -y rsyslog

FROM apt_packages_feewaiver as node_feewaiver

# install node
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
    | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs

# Install Python libs from requirements.txt.
FROM node_feewaiver as python_libs_feewaiver
WORKDIR /app
COPY requirements.txt ./
RUN touch /app/rand_hash
RUN pip install --no-cache-dir -r requirements.txt
# && \
#    rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

# COPY libgeos.py.patch /app/
# RUN patch /usr/local/lib/python3.9/dist-packages/django/contrib/gis/geos/libgeos.py /app/libgeos.py.patch && \
#    rm /app/libgeos.py.patch

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_feewaiver as build_vue_feewaiver

COPY feewaiver ./feewaiver
RUN cd /app/feewaiver/frontend/feewaiver; npm install && \
    cd /app/feewaiver/frontend/feewaiver; npm run build

FROM build_vue_feewaiver as collectstatic_feewaiver

RUN touch /app/.env
COPY manage_fw.py ./
RUN python manage_fw.py collectstatic --noinput

FROM collectstatic_feewaiver as configure_feewaiver

# COPY .git ./
COPY gunicorn.ini ./
COPY timezone /etc/timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    mkdir /app/tmp/ && \
    chmod 777 /app/tmp/

COPY cron /etc/cron.d/dockercron
COPY startup.sh /

# Configure cron (service is started in startup.sh)
RUN chmod 0644 /etc/cron.d/dockercron && \
    crontab /etc/cron.d/dockercron && \
    touch /var/log/cron.log && \
    chmod 755 /startup.sh

# IPYTHONDIR - Will allow shell_plus (in Docker) to remember history between sessions
RUN export IPYTHONDIR=/app/logs/.ipython/

FROM configure_feewaiver as launch_feewaiver

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
