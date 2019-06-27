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

from .utils import is_ipython
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

    if is_ipython():
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

def upload_tar_to_s3(
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
        upload_to_s3(
            destination=destination,
            workspace=tmpfile.name,
            s3_client=s3_client
        ),

def _encode_b64(value):
    return base64.b64encode( value.encode('utf-8') ).decode('ascii')


def _file_to_list(filename):
    if not os.path.isfile(filename):
        return []
    with open(filename) as f:
        return f.read().splitlines()


def current_region():
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
