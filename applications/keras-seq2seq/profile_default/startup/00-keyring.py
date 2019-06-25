import keyring
from extensions import KubernetesKeyring

keyring.set_keyring(KubernetesKeyring())
