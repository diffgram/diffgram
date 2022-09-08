try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *


@routes.route('/api/configs/is-mailer-set')
def mailgun_is_set():
    is_set_mailgun = settings.MAILGUN_KEY and settings.EMAIL_DOMAIN_NAME and settings.EMAIL_VALIDATION
    is_set_smtp_mailer = settings.EMAIL_VALIDATION and settings.EMAIL_VALIDATION and settings.SMTP_HOST \
                         and settings.SMTP_PORT and settings.SMTP_USERNAME and settings.SMTP_PASSWORD

    if is_set_mailgun or is_set_smtp_mailer:
        return jsonify({"mailgun": True})
    return jsonify({"mailgun": False})
