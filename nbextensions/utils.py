from kubernetes import config
import hashlib, requests, os

def sha1(*argv):
    """returns sha1 encoded string. optionally supports salt
    """
    s = ':'.join(argv)
    return hashlib.md5(s.encode()).hexdigest()

def get_md5(fname):
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
        if md5sum == get_md5(download_to):
            print(f"It seems {download_to} has been already downloaded")
            print("Moving on...")
            return
    

    print('Downloading...')
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        fdir = os.path.dirname(download_to)
        if not os.path.isdir(fdir):
            os.makedirs(fdir, exist_ok=True)
            
        with open(download_to, 'wb+') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    print('Done!')

def encode_b64(value):
    return base64.b64encode( value.encode('utf-8') ).decode('ascii')

def is_ipython():
    """Returns whether we are running in notebook."""
    try:
        import IPython
    except ImportError:
        return False
    return True
