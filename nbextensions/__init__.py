import sys
if sys.version_info.major != 3:
    # at present we only support python3 because we want to rely on FStrings and other goodness
    raise ValueError('We only support Python 3; recommended Python 3.6')

from .setup import __version__
from .magics import *
from .keyrings import *
from .pv import use_pvc
import pandas as pd

def _is_ipython():
    """Returns whether we are running in notebook."""
    try:
        import IPython
    except ImportError:
        return False
    return True

def _current_namespace():
    from kubernetes import config as kube_config
    try:
        result = kube_config.list_kube_config_contexts()[1].get(
            'context', {}).get('namespace')
        if result:
            return result
    except (IndexError, FileNotFoundError):
        pass
    try:
        return open('/var/run/secrets/kubernetes.io/serviceaccount/namespace').read()
    except OSError:
        return 'default'

def _configmap_to_ns(name, namespace=_current_namespace(), user_ns=None):
    # here we rely highly rely on lazy imports
    from kfp.compiler._k8s_helper import K8sHelper
    from kubernetes import config as kube_config
    from kubernetes import client as kube_client
    from kubernetes.client.rest import ApiException
    from IPython import get_ipython
    api = kube_client.CoreV1Api(K8sHelper()._api_client)
    try:
        configmap = api.read_namespaced_config_map(name, namespace, exact=True)
        user_ns = user_ns or get_ipython().user_ns
        # raise ValueError(f'Expected error {configmap}a')
        data = dict(configmap.data)
        if 'NAMESPACE' not in user_ns:
            data['NAMESPACE'] = _current_namespace()
        df = pd.DataFrame.from_dict({
                'variable': list(data.keys()),
                'value': list(data.values()),
            })
        display(HTML(f"<i>Implicit variables found in configmap: <b>{name}</b></i><br>{df.to_html(index=False)}"))
        items = {k:v for k,v in data.items() if k not in user_ns}
        if items:
            user_ns.update(items)
    except ApiException as e:
        display(e)
        logging.error(e)
        return

if _is_ipython():
    from os import environ
    from IPython.display import display, HTML
    _configmap_to_ns(environ.get('NB_VARS', 'jupyter-vars'))
