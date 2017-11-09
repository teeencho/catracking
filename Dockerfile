FROM ubuntu:xenial

ENV APP_FOLDER=/tmp/app

RUN apt-get update && apt-get install -qy \
    curl \
    python2.7 \
    python3.5 && \
    curl -s https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py && \
    python3.5 /tmp/get-pip.py

RUN pip install --no-cache-dir \
    tox

RUN useradd -r -ms /bin/bash ubuntu

COPY . ${APP_FOLDER}
RUN chown -R ubuntu ${APP_FOLDER}

USER ubuntu
WORKDIR ${APP_FOLDER}
