# Github Issue Summarization
This is an end-to-end pre-integrated machine learning applicaiton. 
* Training with [Keras](http://keras.io)
* Serving with [Seldon](https://docs.seldon.io/projects/seldon-core/en/latest/workflow/README.html)
* Deployment on Kubernetes with [Flask](http://flask.pocoo.org)

Upon successful completion of these stages, user will get a web application that is able to predict 
Github issue title by reading it's description.

## Introduction

### Problem
Given a dataset of the github issueses used. Where every issue has been processed into a vector. Then it has been then used for 
[Sequence to Sequence](https://nlp.stanford.edu/~johnhew/public/14-seq2seq.pdf) model traing.

### Technologies used:
* Docker registry
* Github
* Jupyter Notebook
* Kubeflow Pipelines
* Keras
* Minio

