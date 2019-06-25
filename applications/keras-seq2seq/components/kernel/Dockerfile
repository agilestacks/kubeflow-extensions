ARG buildFrom=gcr.io/kubeflow-images-public/tensorflow-1.13.1-notebook-cpu:v0.5.0
ARG nbUser=jovyan
FROM ${buildFrom}
ENV LANG C.UTF-8
COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir --upgrade 'pip'
RUN pip3 install --no-cache-dir --upgrade 'https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tarball/master'
RUN pip3 install --no-cache-dir --upgrade 'jupyter_nbextensions_configurator'
USER root
RUN jupyter contrib nbextension install --system
RUN jupyter nbextensions_configurator enable --system
USER ${nbUser}

ENV JUPYTER_CONFIG_DIR /usr/local/etc/jupyter/nbconfig

RUN jupyter nbextension enable codefolding/main
COPY nbconfig $JUPYTER_CONFIG_DIR

RUN cd /tmp && git clone "https://github.com/google/seq2seq.git" && \
    pip3 install --no-cache-dir --upgrade --requirement '/requirements.txt' && \
    rm -rf /tmp/*
