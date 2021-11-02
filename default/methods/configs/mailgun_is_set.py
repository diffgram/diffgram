from methods import routes
from shared.settings import settings

@routes.route('/api/configs/is-mailer-set')
def mailgun_is_set():
    is_set = settings.MAILGUN_KEY and settings.EMAIL_DOMAIN_NAME and settings != 'localhost'
    
    if is_set:
        return "true"
    return "false"
