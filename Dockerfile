FROM python:3.7-buster
LABEL maintainer="Codimp"

RUN apt-get update && \
    apt-get install --no-install-recommends -y dexdump=8.1.0* postgresql-client-11=11* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

RUN useradd -ms /bin/bash exodus

RUN mkdir -p /home/exodus/.config/gplaycli
COPY ./docker.gplaycli.* /home/exodus/.config/gplaycli/
RUN patch /usr/local/lib/python3.7/site-packages/gplaycli/gplaycli.py /home/exodus/.config/gplaycli/docker.gplaycli.patch

COPY ./ /home/exodus/exodus

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R exodus:exodus /home/exodus
USER exodus
WORKDIR /home/exodus/exodus/exodus

CMD ["/entrypoint.sh", "init"]
