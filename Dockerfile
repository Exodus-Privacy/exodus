FROM debian:9
LABEL maintainer="Codimp"

RUN apt-get update && \
    apt-get install -y \
    dexdump \
    python3-dev \
    python3-pip \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    postgresql-client

COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

RUN useradd -ms /bin/bash exodus

RUN mkdir -p /home/exodus/.config/gplaycli && cp /usr/local/lib/python3.5/dist-packages/root/.config/gplaycli/gplaycli.conf /home/exodus/.config/gplaycli/gplaycli.conf

COPY ./ /home/exodus/exodus

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R exodus:exodus /home/exodus
USER exodus
WORKDIR /home/exodus/exodus/exodus

CMD ["/entrypoint.sh", "init"]
