from shared.settings import settings

try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *


def mail_var_is_set(setting_value):
    if setting_value is None or setting_value == 'none' or not setting_value:
        return False
    return True


@routes.route('/api/configs/is-mailer-set')
def mailgun_is_set():
    is_set_mailgun = mail_var_is_set(settings.MAILGUN_KEY) and settings.EMAIL_DOMAIN_NAME and settings.EMAIL_VALIDATION
    print('settings.EMAIL_VALIDATION', settings.EMAIL_VALIDATION)
    print('settings.SMTP_HOST', settings.SMTP_HOST)
    print('settings.SMTP_USERNAME', settings.SMTP_USERNAME)
    print('settings.SMTP_PORT', settings.SMTP_PORT)
    print('settings.SMTP_PASSWORD', settings.SMTP_PASSWORD)
    print('settings.MAILGUN_KEY', settings.MAILGUN_KEY)
    print('settings.EMAIL_DOMAIN_NAME', settings.EMAIL_DOMAIN_NAME)
    print('settings.EMAIL_VALIDATION', settings.EMAIL_VALIDATION)
    is_set_smtp_mailer = mail_var_is_set(settings.EMAIL_VALIDATION) and mail_var_is_set(settings.SMTP_HOST) \
                         and mail_var_is_set(settings.SMTP_PORT) and mail_var_is_set(settings.SMTP_USERNAME) and \
                         mail_var_is_set(settings.SMTP_PASSWORD)

    if is_set_mailgun or is_set_smtp_mailer:
        return jsonify({"mailgun": True})
    return jsonify({"mailgun": False})
