# Kubeflow Pipeline Templates
This is a repo for the Agile Stacks Kubeflow Pipelines templates. It contains end-to-end tutorials for Kubeflow Pipelines, Keras, and Seldon. 

In this tutorial we will introduce reusable Machine Learning Pipelines that can be used as a template for your machine learning scenarios. 

We will cover the following steps:
* Learn how to build pipelines for training, monitoring and deployment of deep learning models.
* Prepare and store training data in S3 buckets or NFS volumes.
* Build, train, optimize, and deploy models from Jupyter notebooks.
* Train Sequence to Sequence NLP model using multiple GPUs.
* Deploy your machine learning models and experiments at scale on AWS Kubernetes service
* Reduce cost with automation, node autoscaling, and AWS spot instances.
* Deploy machine learning models on AWS, GCP, or on-prem hardware.
* Compare results of experiments with monitoring and experiment tracking tools.
* Automate experiment tracking, hyper parameter optimization, model versioning, deployment to production.
* Implement simple web applications and send prediction requests to the deployed models using Seldon or Tensorflow Serving.

Sample pipelines, algorithms, and training data sets are provided for solving common problems such as data cleansing and training on a large amount of samples


## Repository layout

```
tutorials/ - various tutorials and documentation related to the pipeline templates
kernels/ - here we publish Jupyter Notebook custom kernels
applications/ - application templates used to as tutorials and for user application generation by SuperHub
storage/ - Contains storage plugins such as Goofys Flex plugin for S3
nbextensions/ - Jupyter notebook extensions 
```

## Acknowledgments

We will use popular open source frameworks such as Kubeflow, Keras, and Seldon to implement end-to-end ML pipelines that can run on AWS, GCP, or on-premises hardware. The Kubeflow project is designed to simplify the deployment of machine learning projects like Keras and TensorFlow on Kubernetes. These frameworks can leverage multiple GPUs in the Kubernetes cluster to scale machine learning tasks. We will also cover how you can use Kubeflow pipelines to continuously deploy models to production and retrain models on real life data.  By deploying the ML model into real world you will learn from feedback loops and quickly improve the model.  After implementing this tutorial, you will gain knowledge about best practices for deploying ML algorithms and artifacts, and learn about open source software available for production ML lifecycle management.

----

# License
This repositoriy is distributed under Apache 2 ([license text](LICENSE))

