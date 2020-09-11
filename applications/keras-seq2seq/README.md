# Github Issue Summarization
This is an end-to-end ML pipeline built on [Kubeflow](https://www.kubeflow.org/docs/about/kubeflow/) 
* Training with [Keras](http://keras.io)
* Serving with [Seldon](https://docs.seldon.io/projects/seldon-core/en/latest/workflow/README.html)
* Deployment on Kubernetes with [Flask](http://flask.pocoo.org)

Warning: This example stopped working for Kubeflow 1.0.  We are currently working on updated version for Kubeflow 1.x.

Upon successful completion of these stages, user will get a web application that is able to predict 
Github issue title by reading it's description.

## Introduction

### Problem
Given a dataset of the github issueses used. Where every issue has been processed into a vector. Then it is used for 
[Sequence to Sequence](https://nlp.stanford.edu/~johnhew/public/14-seq2seq.pdf) model traing.

### Technologies used:
* Docker registry
* Github
* Jupyter Notebook
* Kubeflow Pipelines
* Keras
* Minio

