import base64
import boto3
import tempfile
import tarfile
import os
import fnmatch

from kubernetes import config as kube_config
from kubernetes import client as kube_client
from kfp.compiler._k8s_helper import K8sHelper
from kubernetes.client.rest import ApiException
from tempfile import NamedTemporaryFile

from os.path import relpath, join, getmtime, getsize
from datetime import datetime

# https://github.com/heroku/kafka-helper/issues/6#issuecomment-365353974
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def upload_to_s3(
        destination,
        workspace='.',
        ignorefile='.dockerignore',
        s3_client=boto3.client('s3')):

    o = urlparse( destination )
    bucket = o.netloc
    prefix = o.path.lstrip('/')
    ignores = _file_to_list(ignorefile)
    count = 0
    total_size = 0

    bucket_keys = s3_client.list_objects(
        Bucket=bucket,
        Prefix=prefix
    ).get('Contents', [])

    bucket_mtimes = {}
    for k in bucket_keys:
        key = k['Key']
        if key.startswith(prefix+'/'):
            key = key[len(prefix)+1:]
        bucket_mtimes[key] = k.get('LastModified', datetime.min).timestamp()

    local_files = _file_list('.', ignores)

    local_files = [
        f for f in local_files \
        if f not in bucket_mtimes
        or bucket_mtimes[f] < getmtime(f)
    ]

    for f in local_files:
        key = join(prefix, f)
        try:
            s3_client.upload_file(f, bucket, key)
            total_size += getsize(f)
            count += 1
        except FileNotFoundError:
            pass

    if _is_ipython():
        import IPython
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
                Params={
                    'Bucket': bucket,
                    'Key': prefix
                },
                ExpiresIn=1800)

        endpoint = s3_client.meta.endpoint_url.rstrip("/")
        if _is_minio(s3_client, bucket):
            url = f"{endpoint}/minio/{bucket}/{prefix}/"
        else:
            url = f"{endpoint}/{bucket}/{prefix}/"

        total_sizeS = _format_bytes(total_size)
        if count == 1:
            countS = f"{count} file"
        else:
            countS = f"{count} files"

        html = f'Uploaded <a href="{url}" target="_blank" >{countS}</a>; transferred: {total_sizeS}'
        IPython.display.display(IPython.display.HTML(html))

def tar_and_upload_to_s3(
        destination,
        workspace='.',
        ignorefile='.dockerignore',
        s3_client=boto3.client('s3')):

    o = urlparse(destination)
    bucket = o.netloc
    key = o.path.lstrip('/')
    ignores = _file_to_list(ignorefile)

    with NamedTemporaryFile(suffix='.tar.gz') as tmpfile:
        with tarfile.open(tmpfile.name, 'w:gz') as tar:
            for f in _file_list('.', ignores):
                try:
                    tar.add(f, arcname=f)
                except FileNotFoundError:
                    pass
        s3_client.upload_file(tmpfile.name, bucket, key)


def create_secret_from_session(
        secret_name='jupyter-awscreds',
        session=boto3.session.Session(),
        namespace=None ):
    creds = session.get_credentials().get_frozen_credentials()
    create_secret(
        secret_name=secret_name,
        access_key=creds.access_key,
        secret_key=creds.secret_key,
        token=creds.token,
        namespace=namespace,
    )


def create_secret(
        secret_name='jupyter-awscreds',
        access_key=None,
        secret_key=None,
        token=None,
        namespace=None ):
    # KFP k8s helper applies incluster config setup if needed
    api = kube_client.CoreV1Api( K8sHelper()._api_client )

    namespace = namespace or current_namespace()
    new_data = {
        'access_key': _encode_b64(access_key),
        'secret_key': _encode_b64(secret_key),
    }
    if token:
        new_data['token'] = _encode_b64(token)

    try:
        secret = api.read_namespaced_secret(secret_name, namespace)
        secret.data.update(new_data)
        api.replace_namespaced_secret(secret_name, namespace, secret)
    except ApiException:
        secret = kube_client.V1Secret(
            metadata = kube_client.V1ObjectMeta(name=secret_name),
            data = new_data,
            type = 'Opaque'
        )
        api.create_namespaced_secret(namespace=namespace, body=secret)


def use_aws_envvars_from_secret(
        secret_name='jupyter-awscreds',
        secret_namespace=None):

    def _use_aws_envvars_from_secret(task):
        api = kube_client.CoreV1Api( K8sHelper()._api_client )
        ns = secret_namespace or current_namespace()
        secret = api.read_namespaced_secret(secret_name, ns)

        if 'access_key' in secret.data:
            task.add_env_variable(
                kube_client.V1EnvVar(
                    name='AWS_ACCESS_KEY_ID',
                    value_from=kube_client.V1EnvVarSource(
                        secret_key_ref=kube_client.V1SecretKeySelector(name=secret_name, key='access_key')
                    )
                )
            )

        if 'secret_key' in secret.data:
            task.add_env_variable(
                kube_client.V1EnvVar(
                    name='AWS_SECRET_ACCESS_KEY',
                    value_from=kube_client.V1EnvVarSource(
                        secret_key_ref=kube_client.V1SecretKeySelector(name=secret_name, key='secret_key')
                    )
                )
            )

        if 'token' in secret.data:
            task.add_env_variable(
                kube_client.V1EnvVar(
                    name='AWS_SESSION_TOKEN',
                    value_from=kube_client.V1EnvVarSource(
                        secret_key_ref=kube_client.V1SecretKeySelector(name=secret_name, key='token')
                    )
                )
            )

        return task

    return _use_aws_envvars_from_secret


def use_aws_region_envvar(region=None):
    if not region:
        region = get_region_from_metadata()

    def _use_aws_region_envvar(task):

        task.add_env_variable(
            kube_client.V1EnvVar(
                name='AWS_REGION',
                value=region
            )
        )

        return task

    return _use_aws_region_envvar


def _encode_b64(value):
    return base64.b64encode( value.encode('utf-8') ).decode('ascii')

def _file_to_list(filename):
    if not os.path.isfile(filename):
        return []
    with open(filename) as f:
        return f.read().splitlines()


def current_namespace():
    try:
        result = kube_config.list_kube_config_contexts()[1].get('context', {}).get('namespace')
        if result:
            return result
    except (IndexError, FileNotFoundError):
        pass

    try:
        return open('/var/run/secrets/kubernetes.io/serviceaccount/namespace').read()
    except OSError:
        return 'default'


def get_region_from_metadata():
    from ec2_metadata import ec2_metadata
    from requests.exceptions import ConnectTimeout

    try:
        return ec2_metadata.region
    except ConnectTimeout:
        return None


def _match(filename, filters):
    for f in filters:
        if fnmatch.fnmatch(filename, f):
            return True
    return False


def _file_list(dir, ignorelist=[]):
    result = list()
    for root, d_names, f_names in os.walk(dir):
        full_names = [relpath(join(root, f)) for f in f_names]
        for n in full_names:
            if not _match(n, ignorelist):
                result.append(n)
    return result


def _is_ipython():
    """Returns whether we are running in notebook."""
    try:
        import IPython
    except ImportError:
        return False

    return True


def _is_minio(s3_client, bucket):
    serv = s3_client.get_bucket_location(Bucket=bucket)\
            .get('ResponseMetadata', {})\
            .get('HTTPHeaders',{})\
            .get('server', "")
    return serv.lower().startswith("minio")


def _format_bytes(bytes_num):
    sizes = [ "B", "KB", "MB", "GB", "TB" ]

    i = 0
    dblbyte = bytes_num

    while (i < len(sizes) and  bytes_num >= 1024):
            dblbyte = bytes_num / 1024.0
            i = i + 1
            bytes_num = bytes_num / 1024

    return str(round(dblbyte, 2)) + " " + sizes[i]
