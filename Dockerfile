FROM python:3.5-stretch
LABEL maintainer="Codimp"

RUN apt-get update && \
    apt-get install --no-install-recommends -y dexdump=7.0.0* postgresql-client-9.6=9.6.15* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

RUN useradd -ms /bin/bash exodus

RUN mkdir -p /home/exodus/.config/gplaycli && cp /usr/local/lib/python3.5/site-packages/root/.config/gplaycli/gplaycli.conf /home/exodus/.config/gplaycli/gplaycli.conf

COPY ./ /home/exodus/exodus

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R exodus:exodus /home/exodus
USER exodus
WORKDIR /home/exodus/exodus/exodus

CMD ["/entrypoint.sh", "init"]
