from kubernetes import config
from uuid import uuid1
from kubernetes import client as k8sc
from os.path import basename, dirname

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

def dockerjson_pv(
        pull_secret,
        name=None, 
        filename='.dockerconfigjson',
        project_to='/kaniko/.docker/config.json'):
    """
    Creates V1Volume volume projection from kubernetes pull secret
    """
    from os.path import basename, dirname
    from kubernetes import client
    
    if not name:
        from uuid import uuid1
        name='vol-' + str(uuid1())[:12]
    
    return k8sc.V1Volume(
        name=name,
        projected=k8sc.V1ProjectedVolumeSource(sources=[
            k8sc.V1VolumeProjection(
                secret=k8sc.V1SecretProjection(
                    name=pull_secret, 
                    items=[k8sc.V1KeyToPath(key=filename, path=basename(project_to))]
                )
            )
        ])
    )
    
def use_pvc(name, mount_to, read_only=False):
    def _get_pvc_volume(pvc_name, task):
        for vol in task.volumes:
                pvc = vol.persistent_volume_claim
                if pvc and pvc.claim_name == name:
                    return pvc
        return None


    """ applies existing PVC to the pod
    """
    def _use_pvc(task):
        from os.path import basename, dirname
        from kubernetes import client

        # we want to reuse pvc if possible
        vol = _get_pvc_volume(name, task)
        if not vol:
            from uuid import uuid1
            vol = client.V1Volume(
                name=str(uuid1())[:12],
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name=name,
                    read_only=read_only
                )
            )
            task.add_volume(vol)

        task.add_volume_mount(
            client.V1VolumeMount(
                name=vol.name,
                mount_path=mount_to
            )
        )
        return task
    return _use_pvc


def use_pull_secret(
        secret_name, 
        filename='.dockerconfigjson', 
        project_to='/kaniko/.docker/config.json'):
    def _use_pull_secret(task):
        return (
            task.add_volume(
                dockerjson_pv(
                    name='registrycreds',
                    pull_secret=secret_name, 
                    filename=filename, 
                    project_to=project_to
                )
            ).add_volume_mount(
                k8sc.V1VolumeMount(
                    name='registrycreds',
                    mount_path=dirname(project_to)
                )
            )
        )
    return _use_pull_secret
