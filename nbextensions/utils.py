from kubernetes import config
import hashlib
import os.path

def sha1(*argv):
    """returns sha1 encoded string. optionally supports salt
    """
    s = ':'.join(argv)
    return hashlib.md5(s.encode()).hexdigest()


def current_namespace():
    try:
        result = config.list_kube_config_contexts()[1].get(
            'context', {}).get('namespace')
        if result:
            return result
    except (IndexError, FileNotFoundError):
        pass

    try:
        return open('/var/run/secrets/kubernetes.io/serviceaccount/namespace').read()
    except OSError:
        return 'default'


def md5sum(filename):
    """Returns md5 sum"""
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download_file(url, download_to, md5sum):
    """Downloads file from remote url"""
    # NOTE the stream=True parameter below

    if os.path.isfile(download_to) and md5sum:
        if md5sum == md5sum(download_to):
            print(f"It seems {download_to} has been already downloaded")
            print("Moving on...")
            return

    print('Downloading...')
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(download_to, 'wb+') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    print('Done!')
