import keyring
import keyring.backend

from ipython_secrets import *
from os import environ
from base64 import b64encode
from kubernetes.client.rest import ApiException
from kubernetes import client as kube_client
from kubernetes import config

from base64 import b64encode, b64decode

import logging

DEFAULT_KUBE_SECRET_NAME = "jupyter-keyring"

class KubernetesKeyring(keyring.backend.KeyringBackend):
    """Simple keyring adapter that uses kubernetes secrets as storage backend
    """

    def __init__(self, secret_name=None, namespace=None):
        self._configure_k8s()
        self.namespace = namespace or self._current_namespace()
        self.api_client = kube_client.ApiClient()
        self.corev1 = kube_client.CoreV1Api(self.api_client)
        self.secret_name = secret_name or environ.get('NB_SECRET_VARS', DEFAULT_KUBE_SECRET_NAME)

    def set_password(self, servicename, username, password):
        api = self.corev1
        b64 = b64encode(password.encode('utf-8')).decode('ascii')
        try:
            secret = api.read_namespaced_secret(
                self.secret_name, self.namespace)
            secret.data[servicename] = b64
            api.replace_namespaced_secret(
                self.secret_name, self.namespace, secret)
        except ApiException:
            secret = _empty_secret(self.secret_name)
            secret.data = {servicename: b64}
            api.create_namespaced_secret(namespace=self.namespace, body=secret)

    def get_password(self, servicename, username):
        api = self.corev1
        try:
            secret = api.read_namespaced_secret(
                self.secret_name, self.namespace)
            if servicename in secret.data:
                return b64decode(secret.data[servicename]).decode('utf-8')
        except ApiException:
            pass
        return None

    def delete_password(self, servicename, username, password):
        api = self.corev1
        try:
            secret = api.read_namespaced_secret(
                self.secret_name, self.namespace)
            if servicename in secret.data:
                val = secret.data.pop(servicename)
                api.replace_namespaced_secret(
                    self.secret_name, self.namespace, secret)
                return b64decode(val).encode('utf-8')
        except ApiException:
            return None

    def _configure_k8s(self):
        try:
            config.load_kube_config()
            logging.info(
                'Found local kubernetes config. Initialized with kube_config.')
        except:
            logging.info(
                'Cannot Find local kubernetes config. Trying in-cluster config.')
            config.load_incluster_config()
            logging.info('Initialized with in-cluster config.')

    def _current_namespace(self):
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


def _empty_secret(secret_name):
    secret = kube_client.V1Secret()
    secret.metadata = kube_client.V1ObjectMeta(name=secret_name)
    secret.type = 'superhub.io/jupyter-keyring'
    secret.data = {}
    return secret
