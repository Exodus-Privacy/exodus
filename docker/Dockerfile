FROM python:3.9-slim-bullseye
LABEL maintainer="Codimp"

RUN apt-get update && apt-get install --no-install-recommends -y \
  dexdump=10.0.0* \
  postgresql-client-13=13* \
  libpq-dev=13.* \
  gcc=4:10.2.* \
  musl-dev=1.2.* \
  libc6-dev=2.* \
  gettext=0.* \
  pipenv=11.* \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# See https://github.com/NoMore201/googleplay-api/pull/145
COPY gpapi/googleplay.py /usr/local/lib/python3.9/site-packages/gpapi/googleplay.py
# See https://github.com/NoMore201/googleplay-api/pull/153
COPY gpapi/config.py /usr/local/lib/python3.9/site-packages/gpapi/config.py

WORKDIR /opt

COPY ./Pipfile* /opt/
RUN pipenv install --ignore-pipfile --system

WORKDIR /exodus/exodus

COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ /exodus

ENTRYPOINT ["/entrypoint.sh"]
CMD ["init"]
