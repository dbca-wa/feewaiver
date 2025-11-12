# syntax = docker/dockerfile:1.2

# Prepare the base environment.
FROM ubuntu:24.04 as builder_base_feewaiver

LABEL maintainer="asi@dbca.wa.gov.au"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Australia/Perth \
    PRODUCTION_EMAIL=True \
    SECRET_KEY="ThisisNotRealKey" \
    NODE_MAJOR=22

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
    wget \
    virtualenv 
    # rm -rf /var/lib/apt/lists/*

# RUN add-apt-repository ppa:deadsnakes/ppa && \
#     apt-get update && \
#     apt-get install --no-install-recommends -y python3.9 python3.9-dev python3.9-distutils && \
#     ln -s /usr/bin/python3.9 /usr/bin/python && \
#     python3.9 -m pip install --upgrade pip && \
#     apt-get install -y rsyslog

FROM apt_packages_feewaiver as node_feewaiver

# install node
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
    | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs

RUN groupadd -g 5000 oim 
RUN useradd -g 5000 -u 5000 oim -s /bin/bash -d /app
RUN mkdir /app 
RUN chown -R oim.oim /app 

COPY timezone /etc/timezone    
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY startup.sh /
RUN chmod 755 /startup.sh

RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/default_script_installer.sh -O /tmp/default_script_installer.sh
RUN chmod 755 /tmp/default_script_installer.sh
RUN /tmp/default_script_installer.sh

# Install Python libs from requirements.txt.
FROM node_feewaiver AS python_libs_feewaiver
WORKDIR /app
USER oim
RUN virtualenv /app/venv
ENV PATH=/app/venv/bin:$PATH
COPY requirements.txt ./
RUN touch /app/rand_hash
RUN git config --global --add safe.directory /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# && \
#    rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_feewaiver AS build_vue_feewaiver

COPY --chown=oim:oim ledger ./ledger
COPY --chown=oim:oim feewaiver ./feewaiver
RUN cd /app/feewaiver/frontend/feewaiver; npm install && \
    cd /app/feewaiver/frontend/feewaiver; npm run build

FROM build_vue_feewaiver AS collectstatic_feewaiver

RUN touch /app/.env
COPY --chown=oim:oim manage_fw.py ./
RUN python3 manage_fw.py collectstatic --noinput

FROM collectstatic_feewaiver AS configure_feewaiver

# # 1. Copy the .git directory temporarily.
# COPY --chown=oim:oim .git ./.git

# # 2. In a single RUN command:
# #    - Generate the hash file from the .git directory.
# #    - Immediately and forcefully remove the .git directory.
# RUN git rev-parse HEAD > GIT_COMMIT_HASH.txt && \
#     rm -rf ./.git

# COPY --chown=oim:oim .git ./.git

COPY --chown=oim:oim gunicorn.ini ./
COPY --chown=oim:oim python-cron ./

# IPYTHONDIR - Will allow shell_plus (in Docker) to remember history between sessions
RUN export IPYTHONDIR=/app/logs/.ipython/

FROM configure_feewaiver AS launch_feewaiver

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
