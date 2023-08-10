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
from urllib.parse import urlparse
from urllib import parse
from urllib.parse import parse_qs
env_adapter = EnvAdapter()


class Service():
    def __init__(self, name, host, port, path_function, is_default=False):
        self.name = name
        self.host = host
        self.port = port
        self.path_function = path_function
        self.is_default = is_default

    def get_url(self):
        return self.host + ":" + str(self.port) + "/"


class Ingress():

    def __init__(self, host=None):

        self.services_list = []
        self.host = host
        self.default_service = None
        self.flask_app = None
        self.port = 8085

        self.set_named_services()
        self.set_default_service()


    def set_named_services(self):
        self.default = Service(
            name = 'default',
            host = self.host,
            port = 8080,
            path_function = None,
            is_default = True
            )

        self.walrus = Service(
            name = 'walrus',
            host = self.host,
            port = 8082,
            path_function = lambda path : True if path[: 10] == "api/walrus" else False
            )

        self.frontend = Service(
            name = 'frontend',
            host = self.host,
            port = 8081,
            path_function = lambda path : True if path[: 3] != "api" or path[: 6] == "static" else False
            )

        self.services_list.extend([self.default, self.walrus, self.frontend])


    def set_default_service(self):
        for service in self.services_list:
            if service.is_default is True:
                self.default_service = service


    def determine_service(self, path):
        service = None
        for service in self.services_list:
            if service.path_function:
                path_result = service.path_function(path)
                if path_result is True:
                    return service

        return self.default_service


    def unreachable_error(self, service):
        error = {
            'error': {
                'service': service.host,
                'port': service.port,
                'message': f'Service is unreachable. Please check the connection to the {service.host}:{service.port} service.'
            }
        }
        return jsonify(error), 503


    def get_path_with_params(self, path):
        url_parsed = urllib.parse.urlparse(request.url)
        path_with_params = f"{path}?{urllib.parse.unquote(url_parsed.query)}"
        return path_with_params


    def build_request(self, url):
        return requests.request(
                method = request.method,
                url = url,
                headers = {key: value for (key, value) in request.headers if key != 'Host'},
                data = request.get_data(),
                cookies = request.cookies,
                allow_redirects = False)


    def route(self, path):
 
        service = self.determine_service(path)

        try:
            path_with_params = self.get_path_with_params(path)

            url = service.get_url() + path_with_params

            self.app.logger.info(f"Service: {service.name} \t Ingress: {ingress.name} \t URL: {url}")

            response = self.build_request(url)

            return self.default_response_formatting(response)

        except requests.exceptions.ConnectionError:
            return self.unreachable_error(service)


    def default_response_formatting(self, response):
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                   if name.lower() not in excluded_headers]
        new_response = Response(response.content, response.status_code, headers)
        return new_response



class BaremetalIngress(Ingress):
    def __init__(self, host='http://127.0.0.1'):
        super().__init__(host)

        self.name = "baremetal"
        self.app = Flask(__name__,
                               static_folder = "../frontend/dist/static")


class DockerComposeIngress(Ingress):
    def __init__(self, host=None):
        super().__init__(host)

        self.name = "Docker Compose"

        self.default.host = 'http://default'
        self.walrus.host = 'http://walrus'     
        self.frontend.host = 'http://frontend'
        self.frontend.port = 80

        self.app = Flask(__name__, 
                               static_url_path = '/dispatcher-static-files')


class Router():

    def __init__(self, ingress : Ingress):

        self.ingress = ingress
        self.allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

        @self.ingress.app.route('/', defaults = {'path': ''}, methods = self.allowed_methods)
        @self.ingress.app.route('/<path:path>',  methods = self.allowed_methods)
        def all_paths_proxy(path):

            return ingress.route(path)


    def prevent_default_logs(self):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)


    def start(self):

        self.prevent_default_logs()

        self.ingress.app.logger.setLevel(logging.INFO)

        self.ingress.app.debug = False
        self.ingress.app.run(host = '0.0.0.0', port = self.ingress.port)

    

def determine_ingress_from_env():
    DOCKER_CONTEXT = env_adapter.bool(os.getenv('DOCKER_CONTEXT', False))
    DIFFGRAM_SYSTEM_MODE = os.getenv('DIFFGRAM_SYSTEM_MODE', None)

    ingress = BaremetalIngress()   # Default
  
    if DIFFGRAM_SYSTEM_MODE != 'testing_e2e':
        if DOCKER_CONTEXT is True:
            ingress = DockerComposeIngress() 
            
    return ingress

ingress = determine_ingress_from_env()
router = Router(ingress)
router.start()
