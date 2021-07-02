# Main entry point for Default Service

from shared.settings import settings

from shared.shared_logger import get_shared_logger
logger = get_shared_logger()

import time
start_time = time.time()

from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import abort
from flask import session
from flask import request
from flask import Response
from flask import redirect

from werkzeug.contrib.fixers import ProxyFix # needed for get_remote_address to get right ip
from threading import Lock
import os, logging, sys
import requests
from flask_sslify import SSLify
from datetime import timedelta


app = Flask('Diffgram',
			static_folder = "../frontend/dist/static",
			template_folder = "./dist")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024    # 50 Mb limit
sslify = SSLify(app, subdomains=True)  

@app.errorhandler(500)
def server_error(e):
	logging.exception('An error occurred during a request.')

	if app.debug == False:
		return "Please try again later", 500

	if app.debug == True:
		return """
		An internal error occurred: <pre>{}</pre>
		See logs for full stacktrace.
		""".format(e), 500

from routes_init import do_routes_importing

do_routes_importing()
from methods import routes as routes_blueprint

app.register_blueprint(routes_blueprint)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)


do_not_log_these_routes = [
	'/api/user/login',
	'/api/v1/user/password/set']

@app.before_request
def log_request_info():
	try:
		if request.path in do_not_log_these_routes:		# sensitive routes
			return
		out = request.get_json(force=True)
		out['path'] = request.path	# Because may not log in line with normal path printing.
		logger.info(out)
	except Exception as e:
		print("Failed to log ", e)


@app.after_request
def apply_security_rules(response):
	response.headers["X-Frame-Options"] = "SAMEORIGIN"
	response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
	response.headers['X-XSS-Protection'] = '1; mode=block'
	return response


@app.route('/docs', defaults={'path' : ''}, methods=['GET'])
@app.route('/docs/', defaults={'path' : ''}, methods=['GET'])
@app.route('/docs/<path:path>', methods=['GET'])
def docs_redirect(path):
	return redirect("https://diffgram.readme.io/docs/" + path, code=301)	


@app.route('/', defaults={'path' : ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all_unnamed(path):
	"""
	"""

	# This routes to vue js
	if app.debug is False and request.method == 'GET':
		return render_template("index.html")

	print("Post request not found:", path)

	return Response("Not found.", status=405, mimetype='application/json')


app.secret_key = settings.SECRET_KEY

from shared.helpers.security import limiter
limiter.init_app(app) # so we don't have to import app varible into limiter file

from shared.data_tools_core import Data_tools
data_tools = Data_tools().data_tools

print("Startup in", time.time() - start_time)

# Debug
if __name__ == '__main__':

	limiter.enabled = False
	settings.NAME_EQUALS_MAIN = True

	app.run(host='0.0.0.0', port=8080, debug=True)
	# CAUTION . app.run() is BLOCKING 
	# code below app.run will not execute!!! 

else:

	app.debug == False
	app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=2)