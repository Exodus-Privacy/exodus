FROM python:3.7-buster
LABEL maintainer="Codimp"

RUN apt-get update && \
    apt-get install --no-install-recommends -y dexdump=8.1.0* postgresql-client-11=11* gettext=0.* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

COPY ./ /exodus

WORKDIR /exodus/exodus

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh", "init"]
