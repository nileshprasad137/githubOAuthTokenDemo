from flask import Flask, request, redirect, url_for
import requests
import config

from uuid import uuid4

CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
REDIRECT_URI = config.REDIRECT_URI

app = Flask(__name__)


@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with GitHub</a>'
    return text % make_authorization_url()


def make_authorization_url():
    state = str(uuid4())
    # Read more about scopes to understand what scopes are available to this OAuth App
    params = {
        "client_id": CLIENT_ID,
        "state": state,
        "scope": "delete_repo,repo",
        "redirect_uri": REDIRECT_URI
    }
    import urllib
    url = "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(params)
    return url


@app.route('/get_token')
def get_access_token():
    code = request.args.get('code')
    token_json = get_token(code)
    access_token = token_json["access_token"]
    # {'access_token': 'token', 'scope': 'delete_repo', 'token_type': 'bearer'}
    # Do something with this access_token
    return redirect(url_for('list_all_repos', access_token=access_token))


@app.route('/list_all_repos/<access_token>')
def list_all_repos(access_token):
    headers = {
        "Authorization": "token " + access_token
    }
    params = {
        "visibility": "private"
    }
    user_repo_url = "https://api.github.com/user/repos"
    response = requests.get(user_repo_url, headers=headers, params=params)
    return response.text


def get_token(code):
    post_data = {"code": code,
                 "client_id": CLIENT_ID,
                 "client_secret": CLIENT_SECRET,
                 "redirect_uri": REDIRECT_URI}
    headers = {
        "Accept": "application/json"
    }

    response = requests.post("https://github.com/login/oauth/access_token",
                             data=post_data,
                             headers=headers)
    print(response.json())
    # token_json = response.json()
    return response.json()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
