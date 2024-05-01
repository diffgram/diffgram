from shared.settings import settings # Importing settings from shared.settings

try:
    from methods.regular.regular_api import * # Trying to import from methods.regular.regular_api
except:
    from default.methods.regular.regular_api import * # If failed, importing from default.methods.regular.regular_api


def mail_var_is_set(setting_value):
    """
    Check if the setting_value is not None, not 'none', and not an empty string.
    If true, return True, else return False.
    """
    if setting_value is None or setting_value == 'none' or not setting_value:
        return False
    return True


@routes.route('/api/configs/is-mailer-set') # Decorator to register the function as a view for the URL
def mailgun_is_set():
    """
    Check if mailgun or smtp_mailer is set in the settings.
    If either is set, return jsonify({"mailgun": True}), else return jsonify({"mailgun": False}).
    """
    is_set_mailgun = mail_var_is_set(settings.MAILGUN_KEY) and settings.EMAIL_DOMAIN_NAME and settings.EMAIL_VALIDATION
    is_set_smtp_mailer = mail_var_is_set(settings.EMAIL_VALIDATION) and mail_var_is_set(settings.SMTP_HOST) \
                         and mail_var_is_set(settings.SMTP_PORT) and mail_var_is_set(settings.SMTP_USERNAME) and \
                         mail_var_is_set(settings.SMTP_PASSWORD)

    if is_set_mailgun or is_set_smtp_mailer:
        return jsonify({"mailgun": True})
    return jsonify({"mailgun": False})

