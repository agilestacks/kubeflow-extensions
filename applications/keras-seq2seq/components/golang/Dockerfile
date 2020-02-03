FROM golang:alpine as builder

RUN apk update && apk upgrade && \
    apk add --no-cache git make sed
COPY csv.go /go/src/gocsv/
WORKDIR /go
RUN go get gocsv

FROM busybox
COPY --from=builder /go/bin/gocsv /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/gocsv"]
