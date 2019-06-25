FROM python:3.6

COPY requirements.txt /requirements.txt

WORKDIR /tmp
RUN apt-get update \
    && apt-get install -y --no-install-recommends python-pandas git \
    && git clone https://github.com/google/seq2seq.git \
    && pip3 install --no-cache-dir -U pip \
    && pip3 install --no-cache-dir -U -r /requirements.txt \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    /usr/share/man /usr/share/doc /usr/share/doc-base /root/.cache

COPY src /src
WORKDIR /src
