FROM alpine:3.17 AS apkeep-download

ENV APKEEP_VERSION=0.15.0

RUN wget https://github.com/EFForg/apkeep/releases/download/${APKEEP_VERSION}/apkeep-x86_64-unknown-linux-gnu -q -O /tmp/apkeep \
  && chmod +x /tmp/apkeep

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

COPY --from=apkeep-download /tmp/apkeep /usr/local/bin/apkeep

WORKDIR /opt

COPY ./Pipfile* /opt/
RUN pipenv install --ignore-pipfile --system

WORKDIR /exodus/exodus

COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ /exodus

ENTRYPOINT ["/entrypoint.sh"]
CMD ["init"]
