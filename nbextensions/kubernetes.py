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
        from os.path import basename, dirname
        from kubernetes import client as k8sc

        return (
            task.add_volume(
                k8sc.V1Volume(
                    name='registrycreds',
                    projected=k8sc.V1ProjectedVolumeSource(sources=[
                        k8sc.V1VolumeProjection(
                            secret=k8sc.V1SecretProjection(
                                name=secret_name, 
                                items=[k8sc.V1KeyToPath(key=filename, path=basename(project_to))]
                            )
                        )
                    ])
                )
            ).add_volume_mount(
                k8sc.V1VolumeMount(
                    name='registrycreds',
                    mount_path=dirname(project_to)
                )
            )
        )

    return _use_pull_secret
