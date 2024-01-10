FROM rust:1.75.0-slim-bookworm AS apkeep-build

ENV APKEEP_VERSION=0.15.0
ENV OPENSSL_VERSION=1.1.1w

# Workaround to build Apkeep (see https://github.com/Exodus-Privacy/exodus/issues/598)

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential=12.* \
  ca-certificates=202* \
  curl=7.* \
  pkg-config=1.* \
  wget=1.* \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

## Build OpenSSL

RUN wget https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz -q -O /tmp/openssl-${OPENSSL_VERSION}.tar.gz \
  && tar xfvz /tmp/openssl-${OPENSSL_VERSION}.tar.gz --directory /tmp/
WORKDIR /tmp/openssl-${OPENSSL_VERSION}/
RUN ./config --prefix=/opt/openssl --openssldir=/opt/openssl \
  && make \
  && make test \
  && make install_sw

## Build Apkeep

RUN wget https://github.com/EFForg/apkeep/archive/refs/tags/${APKEEP_VERSION}.tar.gz -q -O /tmp/apkeep-${APKEEP_VERSION}.tar.gz \
  && tar -xzf /tmp/apkeep-${APKEEP_VERSION}.tar.gz -C /tmp/ \
  && rm /tmp/apkeep-${APKEEP_VERSION}.tar.gz
WORKDIR /tmp/apkeep-${APKEEP_VERSION}
RUN PATH=/opt/openssl/bin:$PATH LD_LIBRARY_PATH=/opt/openssl/lib OPENSSL_STATIC=1 OPENSSL_INCLUDE_DIR=/opt/openssl/include/ OPENSSL_LIB_DIR=/opt/openssl/lib/ OPENSSL_DIR=/opt/openssl/ cargo build --release \
  && chmod +x target/release/apkeep \
  && mv target/release/apkeep /opt/apkeep

FROM python:3.11-slim-bookworm
LABEL maintainer="Codimp"

RUN apt-get update && apt-get install --no-install-recommends -y \
  dexdump=11.0.0* \
  postgresql-client-15=15* \
  libpq-dev=15.* \
  gcc=4:12.2.* \
  musl-dev=1.2.* \
  libc6-dev=2.* \
  gettext=0.* \
  pipenv=2022.12.* \
  libssl3=3.* \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY --from=apkeep-build /opt/openssl /opt/openssl
COPY --from=apkeep-build /opt/apkeep /usr/local/bin/apkeep
RUN ln -s /usr/lib/ssl/certs /opt/openssl/certs

WORKDIR /opt

COPY ./Pipfile* /opt/
RUN pipenv install --ignore-pipfile --system

WORKDIR /exodus/exodus

COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ /exodus

ENTRYPOINT ["/entrypoint.sh"]
CMD ["init"]
