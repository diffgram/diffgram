# OPENCORE - ADD
from flask import Flask
from flask import redirect
import requests
from flask import request
from flask import Response
from flask import jsonify
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
    app = Flask(__name__, static_url_path = '/dispatcher-static-files')
app.debug = True


def route_same_host(path):
    # Default host
    host = 'http://127.0.0.1:8080/'
    host_reached = 'default'
    url_parsed = urllib.parse.urlparse(request.url)
    path_with_params = f"{path}?{urllib.parse.unquote(url_parsed.query)}"
    # Walrus
    if path[: 10] == "api/walrus":
        host_reached = 'walrus'
        host = 'http://127.0.0.1:8082/'

    # JS local dev server
    if path[: 3] != "api" or path[: 6] == "static":
        host_reached = 'frontend'
        return requests.get(f"http://localhost:8081/{path_with_params}").text

    # https://stackoverflow.com/questions/6656363/proxying-to-another-web-service-with-flask

    try:
        resp = requests.request(
            method = request.method,
            url = host + path_with_params,
            headers = {key: value for (key, value) in request.headers if key != 'Host'},
            data = request.get_data(),
            cookies = request.cookies,
            allow_redirects = False)
    except requests.exceptions.ConnectionError:
        error = {
            'error': {
                'service': host_reached,
                'host': host,
                'message': 'Service is unreachable. Please check the connection to the {} service.'.format(
                    host_reached)
            }
        }
        return jsonify(error), 503

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response


def route_multi_host(path):
    # Default host
    host = 'http://default:8080/'
    host_reached = 'default'
    logging.warning("MULTI HOST {path}")
    url_parsed = urllib.parse.urlparse(request.url)
    path_with_params = f"{path}?{urllib.parse.unquote(url_parsed.query)}"
    # Walrus

    logging.warning(f"MULTI path_with_params {path_with_params}")
    if path[: 10] == "api/walrus":
        host_reached = 'walrus'
        host = 'http://walrus:8082/'

    # JS local dev server
    if path[:3] != "api":
        host_reached = 'frontend'
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
    try:
        resp = requests.request(
            method = request.method,
            url = host + path_with_params,
            headers = {key: value for (key, value) in request.headers if key != 'Host'},
            data = request.get_data(),
            cookies = request.cookies,
            allow_redirects = False)
    except requests.exceptions.ConnectionError:
        error = {
            'error': {
                'service': host_reached,
                'host': host,
                'message': 'Service is unreachable. Please check the connection to the {} service.'.format(
                    host_reached)
            }
        }
        return jsonify(error), 503
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


@app.route('/', defaults = {'path': ''}, methods = ['GET', 'POST'])
@app.route('/<path:path>', methods = ['GET', 'POST'])
def _proxy(path):
    print(f"_proxy:*--------> {path}")
    logging.warning(f"_proxy:*--------> {path}")
    if SAME_HOST:
        print('route_same_host')
        return route_same_host(path)
    else:
        print('route_multi_host')
        return route_multi_host(path)


app.run(host = '0.0.0.0', port = 8085)
