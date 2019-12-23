DOCKERFILE := set-me-please
IMAGE := docker.io/agilestacks/jupyter-$(shell basename -- $(dir $(DOCKERFILE)))

all:
	@ find . -name Dockerfile  -d -maxdepth 2 \
		-exec $(MAKE) build push DOCKERFILE={} \;

build-all:
	@ find . -name Dockerfile  -d -maxdepth 2 \
        -exec $(MAKE) build DOCKERFILE={} \;

build:
	docker build -t $(IMAGE) -f $(DOCKERFILE) $(dir $(DOCKERFILE))

push:
	docker push $(IMAGE)

.DEFAULT := all
.PHONY := push build all
