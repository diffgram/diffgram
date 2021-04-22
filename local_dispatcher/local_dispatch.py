# OPENCORE - ADD
from flask import Flask
from flask import redirect
import requests
from flask import request
from flask import Response
import urllib.parse
import logging
logger = logging.getLogger()
import os
from env_adapter import EnvAdapter
env_adapter = EnvAdapter()

SAME_HOST = os.getenv('SAME_HOST', True)
SAME_HOST = env_adapter.bool(SAME_HOST)

print('host', SAME_HOST)

if SAME_HOST:
    app = Flask(__name__,
                static_folder = "../frontend/dist/static")
else:
    # In this context the dispatcher is on a separate container and does not have access to static folder.
    app = Flask(__name__, static_url_path='/dispatcher-static-files')
app.debug = True


def route_same_host(path):
    # Default host
    host = 'http://127.0.0.1:8080/'

    url_parsed = urllib.parse.urlparse(request.url)
    path_with_params = '{}?{}'.format(path, urllib.parse.unquote(url_parsed.query))
    # Walrus
    if path[: 10] == "api/walrus":
        host = 'http://127.0.0.1:8082/'

    # JS local dev server
    if path[: 3] != "api" or path[: 6] == "static":
        return requests.get('http://localhost:8081/{}'.format(path_with_params)).text

    # https://stackoverflow.com/questions/6656363/proxying-to-another-web-service-with-flask
    resp = requests.request(
        method = request.method,
        url = host + path_with_params,
        headers = {key: value for (key, value) in request.headers if key != 'Host'},
        data = request.get_data(),
        cookies = request.cookies,
        allow_redirects = False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


def route_multi_host(path):
    # Default host
    host = 'http://default:8080/'
    logging.warning('MULTI HOST {}'.format(path))
    url_parsed = urllib.parse.urlparse(request.url)
    path_with_params = '{}?{}'.format(path, urllib.parse.unquote(url_parsed.query))
    # Walrus

    logging.warning('MULTI path_with_params {}'.format(path_with_params))
    if path[: 10] == "api/walrus":
        host = 'http://walrus:8082/'

    print('PATHHH', path_with_params)
    # JS local dev server
    if path[:3] != "api":
        logging.warning('FRONTENDDD')
        host = 'http://frontend:80/'
        resp = requests.request(
            method = request.method,
            url = host + path_with_params,
            headers = {key: value for (key, value) in request.headers if key != 'Host'},
            data = request.get_data(),
            cookies = request.cookies,
            allow_redirects = False)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response

    # https://stackoverflow.com/questions/6656363/proxying-to-another-web-service-with-flask
    resp = requests.request(
        method = request.method,
        url = host + path_with_params,
        headers = {key: value for (key, value) in request.headers if key != 'Host'},
        data = request.get_data(),
        cookies = request.cookies,
        allow_redirects = False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


@app.route('/', defaults = {'path': ''}, methods = ['GET', 'POST'])
@app.route('/<path:path>', methods = ['GET', 'POST'])
def _proxy(path):
    # TODO could switch the path thing to be "diffgram.com"
    # if want to run front end with production end points
    # (or could use a staging endpoint here too...)
    print('_proxy:*--------> {}'.format(path))
    logging.warning('_proxy:*--------> {}'.format(path))
    if SAME_HOST:
        print('route_same_host')
        return route_same_host(path)
    else:
        print('route_multi_host')
        return route_multi_host(path)


app.run(host = '0.0.0.0', port = 8085)
