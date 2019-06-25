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


