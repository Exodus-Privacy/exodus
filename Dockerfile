FROM python:3.7-slim-buster
LABEL maintainer="Codimp"

RUN apt-get update && apt-get install --no-install-recommends -y \
  dexdump=8.1.0* \
  postgresql-client-11=11* \
  libpq-dev=11.* \
  gcc=4:8.3.* \
  musl-dev=1.1.* \
  libc6-dev=2.* \
  gettext=0.* \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

COPY ./ /exodus

WORKDIR /exodus/exodus

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh", "init"]
