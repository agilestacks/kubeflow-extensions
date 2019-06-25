from kubernetes import config

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
