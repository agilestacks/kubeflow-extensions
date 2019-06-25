from .kubernetes import *
import keyring

keyring.set_keyring(KubernetesKeyring())
