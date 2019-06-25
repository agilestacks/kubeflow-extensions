import os
from IPython import get_ipython
from shutil import copy2
from numpy import savetxt

def is_ipython():
    """Returns whether we are running in notebook.
    """
    try:
        import IPython
    except ImportError:
        return False
    return (get_ipython() is not None)

def get_value(key, default=None):
    result = None
    if is_ipython():
        result=get_ipython().user_ns.get(key)
    return result or os.environ.get(key, default)

def get_value_as_int(key, default:int=0):
    return int( get_value(key) or 0 )

def get_value_as_float(key, default:float=0.0):
    return float( get_value(key) or 0.0 )

def copy(src, dest):
    mkdirs_f(dest)
    print(f"Copy to {dest}")
    copy2(src, dest)

def save_list(fname, list):
    mkdirs_f(fname)
    print(f"Saving {fname}")
    with open(fname, 'w') as f:
        for item in list:
            f.write("%s " % item)

def save_text(fname, text):
    mkdirs_f(fname)
    print(f"Saving {fname}")
    with open(fname, "w") as f:
        f.write(text)

def mkdirs_f(fname):
    dirname = os.path.dirname(fname)
    dirname = os.path.abspath(dirname)
    os.makedirs(dirname, exist_ok=True)
