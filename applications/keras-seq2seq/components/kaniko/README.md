# Kaniko Op Pipeline step

This is a Kubeflow Pipeline step component that executes a docker build with Kaniko as part of distributed training.

## Prereqs

1. Install minio and create a bucket (bucket name used here will be : myhappybucket)

2. Create a secret associated with your bucket
```yaml
apiVersion: v1
kind: Secret
type: superhub.io/jupyter-keyring
metadata:
  name: myhappybucket-nb-keyring
stringData:
  aws_access_key_id: "changemeplease"
  aws_secret_access_key: "changemeplease"
```

2. Install Goofys FS Persistence Volume Driver

Please make sure that goofy's FS PV has been instaled. Quickest way to install. Easiest way to execute manifest below with `kubectl` configured for your Kubernetes cluster

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: goofysflex
  labels:
    app: goofysflex
spec:
  selector:
    matchLabels:
      app: goofysflex
  updateStrategy:
    type: RollingUpdate
  template:
    metadata:
      name: goofysflex
      labels:
        app: goofysflex
    spec:
      initContainers:
      - name: install
        image: docker.io/agilestacks/s3fs:latest
        imagePullPolicy: Always
        args: ["export", "/flexmnt"]
        volumeMounts:
        - mountPath: /flexmnt
          name: flexvolume-plugindir
      containers:
      - name: pause
        image: gcr.io/google-containers/pause
      volumes:
      - name: flexvolume-plugindir
        hostPath:
          path: /var/lib/kubelet/volumeplugins
```

3. Install Goofys FS Persistence Volume Driver

```yaml
---
kind: PersistentVolume
apiVersion: v1
metadata:
  name: myhappybucket-pv
  labels:
    type: fuse
    bucket: myhappybucket
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 40Gi
  volumeMode: Filesystem
  # you might want to specify here default storage class name
  # storageClassName: 
  flexVolume:
    driver: "goofysflex"
    secretRef:
      name: bucket-kubeflow-pipelines
    options:
      # Required
      bucket: kubeflow-pipelines
      endpoint: "http://minio.svc:9000"
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: myhappybucket-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  storageClassName: # you may put name of your default storage class here
  resources:
    requests:
      # requiremenets from Kubernetes
      storage: 40Gi
  selector:
    matchLabels:
      type: fuse
      # name of your bucket in minio
      bucket: myhappybucket
```

## Usage Scenario


Here is a simplistic snippet how to run a single job that builds a docker image and pushes 
```python
%reload_ext nbextensions
from nbextensions.pv import use_pvc
import nbextensions

kaniko_op = load_component_from_file('components/kaniko/deploy.yaml')

@dsl.pipeline(
  name='Pipeline images',
  description='Build images that will be used by the pipeline'
)
def build_image(
        image, 
        context=None, 
        dockerfile: dsl.PipelineParam=dsl.PipelineParam(name='dockerfile', value='Dockerfile')):
    dockerjson = dockerjson_pv(pull_secret=DOCKER_REGISTRY_PULL_SECRET)
    kaniko_op(
        image=image,
        dockerfile=dockerfile,
        context=context
    ).add_pvolumes({
        '/mnt/s3': dsl.PipelineVolume(pvc="myhappybucket-pvc"),
        '/kaniko/.docker': dsl.PipelineVolume(volume="dockerregistrypullsecret"),
    })
        
Compiler().compile(build_image, 'argo-kaniko.yaml')
nbextensions.utils.patch_pvolumes('argo-kaniko.yaml')

# Copy docker files (and other artifacts to) to the `myhappybuccket/build-image-here`

run = client.run_pipeline(
    exp.id, f'Build image, 'argo-kaniko.yaml', 
    params={
        'image': "myhappyimage:latest",
        'context': "./build-image-herre"
    })
    
client.wait_for_run_completion(run.id, timeout=720).run
```

