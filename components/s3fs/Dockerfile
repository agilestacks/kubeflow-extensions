ARG FROM=busybox
ARG VERSION=dev

##########
FROM golang AS go2
RUN go get github.com/kahing/goofys
RUN go install github.com/kahing/goofys
##########
FROM golang AS go1
COPY src /go/src
WORKDIR /go/src/goofysflex
RUN make install compile VERSION=${VERSION}

########
FROM alpine:latest AS fusermount
ARG FUSE_VERSION=2.9.7
RUN apk --update add --virtual build-dependencies --no-cache \
	build-base \
	ca-certificates \
	wget \
	gnupg \
	&& update-ca-certificates \
	&& rm -rf /var/cache/apk/* \
	&& cd / \
	&& wget https://github.com/libfuse/libfuse/releases/download/fuse-${FUSE_VERSION}/fuse-${FUSE_VERSION}.tar.gz \
	&& wget https://github.com/libfuse/libfuse/releases/download/fuse-${FUSE_VERSION}/fuse-${FUSE_VERSION}.tar.gz.asc \
	&& gpg --keyserver hkps.pool.sks-keyservers.net --recv-key 3C4E599F \
	&& gpg fuse-${FUSE_VERSION}.tar.gz.asc \
	&& tar zxf fuse-${FUSE_VERSION}.tar.gz \
	&& cd fuse-${FUSE_VERSION} \
	&& ./configure \
	&& make -C util LDFLAGS="-all-static -Wl,-v -Wl,--strip-all" V=1 fusermount \
	&& cp util/fusermount /usr/local/bin

######
FROM ${FROM}

ARG TINI_VERSION="0.16.1"
ADD https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini-static-amd64 /usr/bin/tini
COPY --from=go1 /goofysflex /usr/bin/goofysflex
COPY --from=go2 /go/bin/goofys /usr/bin/goofys
COPY --from=fusermount /usr/local/bin/fusermount /usr/bin/fusermount
COPY  dummy.sh /usr/bin/dummy
COPY  export.sh /usr/bin/export
RUN chmod +x /usr/bin/*

ENTRYPOINT ["tini", "--"]
