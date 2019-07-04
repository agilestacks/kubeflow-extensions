from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring, construct_parser)
from IPython.core.magic import (line_magic, cell_magic, line_cell_magic, Magics, magics_class)
from IPython import get_ipython
from IPython.display import (display, HTML, Code, Markdown)

from kfp.compiler._k8s_helper import K8sHelper
from kubernetes import config as kube_config
from kubernetes import client as kube_client
from kubernetes.client.rest import ApiException

from ..kubernetes import current_namespace

import os
import pandas as pd

@magics_class
class NBVarsMagics(Magics):

    @magic_arguments()
    @argument('configmap',
        nargs='*',
        default=None,
        help="Name of the configmap to where to look"
    )
    @argument('-n', '--namespace',
        default=None,
        help="Kubernetes namespace"
    )
    @argument('-v', '--verbose',
        default=False,
        help="Print output",
        action='store_true',
    )
    @line_magic
    def load_nbvars(self, line):
        """Loads envvars into current notebook
        """
        args = parse_argstring(self.load_nbvars, line)
        namespace = args.namespace or current_namespace()
        name = args.configmap or os.environ.get('NB_VARS', 'jupyter-vars')
        user_ns = get_ipython().user_ns
        display(Markdown(f"Loading notebook variables from configmap: `{namespace}/{name}`"))
        try:
            load_nbvars(name, namespace, )
        except ApiException as e:
            display(Code(f"Error reading configmap {namespace}/{name}: {e.status}, {e.reason}"))
            return e

def load_nbvars(configmap, namespace=current_namespace(), user_ns=get_ipython().user_ns):
    """Loads envvars into current notebook
    """
    api = kube_client.CoreV1Api(K8sHelper()._api_client)
    resource = api.read_namespaced_config_map(configmap, namespace, exact=True)
    data = dict(resource.data)
    if 'NAMESPACE' not in user_ns:
        data['NAMESPACE'] = current_namespace()
    # we filter variables unless declared in user namespace             
    items = {k:v for k,v in data.items() if k not in user_ns}
    if items:
        user_ns.update(items)
       
        df = pd.DataFrame.from_dict({
            'variable': list(items.keys()),
            'value': list(items.values()),
        })
        display(HTML(df.to_html(index=False)))
    else:
        display(Markdown('All notebook variables has been already loaded'))
    return items
