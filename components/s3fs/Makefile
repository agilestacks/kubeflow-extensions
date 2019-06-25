.DEFAULT_GOAL := compile
IMAGE         := "agilestacks/s3fs"
VERSION       := $(shell git rev-parse --short HEAD)
NAMESPACE     ?= kube-system

kubectl       := kubectl --context="$(DOMAIN_NAME)" --namespace="$(NAMESPACE)"

compile install:
	$(MAKE) -C src/goofysflex VERSION=$(VERSION) "$@"

build:
	docker build --build-arg VERSION=$(VERSION) -t $(IMAGE) .

push:
	docker push $(IMAGE)

namespace:
	- $(kubectl) create namespace $(NAMESPACE)

deploy: namespace
	- $(kubectl) create -f install.yaml

undeploy:
	- $(kubectl) delete -f install.yaml

