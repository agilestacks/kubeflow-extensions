.DEFAULT_GOAL := compile

file := $(GOBIN)/$(notdir $(CURDIR))
VERSION := $(shell git rev-parse --short HEAD)

compile:
	go build -ldflags "-X main.version=$(VERSION)" -v -o $(file) .

install:
#	go get -u k8s.io/client-go/...
	go get -u github.com/spf13/cobra/cobra
	go get github.com/spf13/viper
	go get github.com/sirupsen/logrus
	go get github.com/heirko/go-contrib/logrusHelper
	go get github.com/heralight/logrus_mate/hooks/file
	go get github.com/go-errors/errors

clean:
	rm -rf $(file)
