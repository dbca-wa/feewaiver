# Prepare the base environment.
ARG IMAGE_TAG
ARG IMAGE_NAME
FROM ghcr.io/dbca-wa/docker-apps-dev:ubuntu_2604_base_python_node AS builder_base_feewaiver
ARG IMAGE_TAG
ARG IMAGE_NAME
RUN echo "Building version: $IMAGE_TAG for $IMAGE_NAME"
ENV CONTAINER_IMAGE_TAG=${IMAGE_TAG}
ENV CONTAINER_IMAGE_NAME=${IMAGE_NAME}
ENV VIRTUAL_ENV=/app/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
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

RUN apt-get update 
RUN apt-get upgrade -y
    

FROM apt_packages_feewaiver as node_feewaiver

RUN groupadd -g 5000 oim 
RUN useradd -g 5000 -u 5000 oim -s /bin/bash -d /app
RUN mkdir /app 
RUN chown -R oim.oim /app 

COPY timezone /etc/timezone    
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY startup.sh /
RUN chmod 755 /startup.sh

# Install Python libs from requirements.txt.
FROM node_feewaiver AS python_libs_feewaiver
WORKDIR /app
USER oim

# RUN virtualenv /app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH=/app/venv/bin:$PATH
COPY requirements.txt ./
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

# COPY --chown=oim:oim .git ./.git

COPY --chown=oim:oim gunicorn.ini ./
COPY --chown=oim:oim python-cron ./

# IPYTHONDIR - Will allow shell_plus (in Docker) to remember history between sessions
RUN export IPYTHONDIR=/app/logs/.ipython/

FROM configure_feewaiver AS launch_feewaiver

# Cleanup
USER root
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/refs/heads/main/wagov_utils/bin/package_cleanup_2604.sh -O /tmp/package_cleanup_2604.sh
RUN chmod 755 /tmp/package_cleanup_2604.sh
RUN /tmp/package_cleanup_2604.sh
USER oim

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
