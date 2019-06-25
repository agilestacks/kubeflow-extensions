"""
Simple app that parses predictions from a trained model and displays them.
"""

import os
import re
import random

import requests
import pandas as pd
from flask import Flask, json, render_template, request, g, jsonify
from requests.auth import HTTPBasicAuth

APP = Flask(__name__)
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
SAMPLE_DATA = os.environ.get('SAMPLE_DATA', '/data/sample.csv')
SERVER_ADDR = os.environ['SERVER_ADDR']

OAUTH_KEY = os.environ.get('OAUTH_KEY', '')
OAUTH_SECRET = os.environ.get('OAUTH_SECRET', '')

def get_issue_body(issue_url):
    issue_url = re.sub('.*github.com/', 'https://api.github.com/repos/', issue_url)
    return requests.get(issue_url, headers={'Authorization': 'token {}'.format(GITHUB_TOKEN)}).json()['body']

def get_token():
    """returns bearer token for seldon deployment
    """
    response = requests.post(
                f"http://{SERVER_ADDR}/oauth/token",
                auth=HTTPBasicAuth(OAUTH_KEY, OAUTH_SECRET),
                data={'grant_type': 'client_credentials'})
    return response.json()["access_token"]

@APP.route("/")
def index():
    """Default route.
    Placeholder, does nothing.
    """
    return render_template("index.html")


@APP.route("/summary", methods=['POST'])
def summary():
    """Main prediction route.
    Provides a machine-generated summary of the given text. Sends a request to a live
    model trained on GitHub issues.
    """
    if request.method == 'POST':
        issue_text = request.form["issue_text"]
        issue_url = request.form["issue_url"]
        if issue_url:
                issue_text = get_issue_body(issue_url)
        url = f"http://{SERVER_ADDR}/api/v0.1/predictions"
        token = get_token()
        headers = {
            'content-type': 'application/json',
            'Authorization': f"Bearer {token}"
        }
        json_data = {"data": {"ndarray": [[issue_text]]}}
        response = requests.post(url=url, headers=headers, data=json.dumps(json_data))
        response_json = json.loads(response.text)
        issue_summary = response_json["data"]["ndarray"][0][0]
        return jsonify({'summary': issue_summary, 'body': issue_text})

    return ('', 204)


@APP.route("/random_github_issue", methods=['GET'])
def random_github_issue():
    github_issues = getattr(g, '_github_issues', None)
    if github_issues is None:
        github_issues = g._github_issues = pd.read_csv(SAMPLE_DATA).body.tolist()
    return jsonify({
        'body':
        github_issues[random.randint(0, len(github_issues) - 1)]
    })


if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=80)
