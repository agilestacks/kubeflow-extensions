def use_pull_secret_projection(
        secret_name, 
        filename='.dockerconfigjson', 
        project_to='/kaniko/.docker/config.json'):
    def _use_pull_secret_projection(task):
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

    return _use_pull_secret_projection
