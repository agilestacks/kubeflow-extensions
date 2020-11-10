FROM alpine as blobs
ARG YQ_VERSION="3.3.2"
ARG EKSCTL_VERSION="0.30.0"
WORKDIR /usr/local/bin/
RUN apk update && \
	apk add gzip tar curl
RUN FILE=yq && \
	test ! -f $FILE && curl -J -L -o $FILE \
	https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64
RUN FILE=eksctl_Linux_amd64.tar.gz && \
	test ! -f $FILE && curl -JLO \
	https://github.com/weaveworks/eksctl/releases/download/${EKSCTL_VERSION}/$FILE && \
	tar xvzf $FILE eksctl && \
	mv eksctl /usr/local/bin

RUN chmod +x /usr/local/bin/*

FROM gcr.io/kubeflow-images-public/tensorflow-2.1.0-notebook-cpu:1.0.0
EXPOSE 8888
ARG PYVER=3.6
# gid=100(users)
ENV NB_GID 100
ENV HOME               /home/jovyan
ENV LANG               C.UTF-8
ENV PATH               "$PATH:$HOME/.local/bin"
ENV IPYTHONDIR         "$HOME/.ipython "
ENV JUPYTER_CONFIG_DIR "$HOME/.nbconfig"
ENV PYTHONPATH         "$HOME/local/lib/python${PYVER}/site-packages"

USER root
# avoids permission problem like: /home/jovyan/.local
COPY --from=blobs /usr/local/bin /usr/local/bin
RUN chown -R $NB_UID:$NB_GID $HOME
RUN apt-get update -y \
	&& apt-get install -yqq \
		jq \
		libgl1-mesa-glx \
		build-essential \
		cython \
		cython3 \
	&& rm -rf /var/lib/apt/lists/*

RUN curl -sLo /usr/local/bin/hub https://controlplane.agilestacks.io/dist/hub-cli/hub.linux_amd64 \
	&& chmod +x /usr/local/bin/hub
USER $NB_USER
COPY requirements.txt /requirements.txt
RUN hub extensions install
RUN pip3 install --user --no-cache-dir -U 'pip'
RUN pip3 install --user --no-cache-dir -U -r '/requirements.txt'

RUN jupyter contrib nbextension install --user
RUN jupyter nbextensions_configurator enable --user
RUN jupyter nbextension enable codefolding/main
RUN jupyter nbextension enable varInspector/main
