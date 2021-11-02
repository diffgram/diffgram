try:
	from methods.regular.regular_api import *
except:
	from default.methods.regular.regular_api import *

from shared.helpers.security import limiter
from methods import routes

@routes.route('/api/configs/is-mailer-set')
def mailgun_is_set():
    is_set = settings.MAILGUN_KEY and settings.EMAIL_DOMAIN_NAME and settings != 'localhost'
    
    if is_set:
        return jsonify({"mailgun": "true"})
    return jsonify({"mailgun": "false"})
