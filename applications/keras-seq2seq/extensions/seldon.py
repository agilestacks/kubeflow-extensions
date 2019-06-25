import requests
from requests.auth import HTTPBasicAuth

def get_token(server, oauth_key='oauth-key', oauth_secret='oauth-secret'):
    """returns bearer token for seldon deployment
    """
    response = requests.post(
                f"http://{server}/oauth/token",
                auth=HTTPBasicAuth(oauth_key, oauth_secret),
                data={'grant_type': 'client_credentials'})
    return response.json()["access_token"]


def prediction(server, payload, token, version='v0.1'):
    """returns bearer token for seldon deployment
    """
    response = requests.post(
                f"http://{server}/api/{version}/predictions",
                headers={'Authorization': f"Bearer {token}"},
                json=payload)
    return response.json()
