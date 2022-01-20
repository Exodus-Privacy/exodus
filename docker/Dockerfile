FROM python:3.7-slim-buster
LABEL maintainer="Codimp"

WORKDIR /exodus/exodus

ENTRYPOINT ["/entrypoint.sh"]
CMD ["init"]

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

# See https://github.com/NoMore201/googleplay-api/pull/145
COPY gpapi/googleplay.py /usr/local/lib/python3.7/site-packages/gpapi/googleplay.py
# See https://github.com/NoMore201/googleplay-api/pull/153
COPY gpapi/config.py /usr/local/lib/python3.7/site-packages/gpapi/config.py

COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/requirements.txt

COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ /exodus
