try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.permissions.super_admin_only import Super_Admin


@routes.route('/api/v1/admin/install/info',
              methods = ['GET'])
@Super_Admin.is_super()
def api_admin_install_info():
    with sessionMaker.session_scope() as session:
        install_info = serialize_public_env_variables()

        return jsonify(install_info = install_info), 200


def serialize_public_env_variables():
    out = {}

    general = {
        'DIFFGRAM_SYSTEM_MODE': settings.DIFFGRAM_SYSTEM_MODE,
        'DIFFGRAM_VERSION_TAG': settings.DIFFGRAM_VERSION_TAG,
        'DIFFGRAM_HOST_OS': settings.DIFFGRAM_HOST_OS,
        'URL_BASE': settings.URL_BASE,
        'RUNNING_LOCALLY': settings.RUNNING_LOCALLY,
        'DATABASE_URL': bool(settings.DATABASE_URL),
        'DATABASE_CONNECTION_POOL_SIZE': settings.DATABASE_CONNECTION_POOL_SIZE,
        'WALRUS_SERVICE_URL_BASE': settings.WALRUS_SERVICE_URL_BASE,
        'EVENTHUB_URL': settings.EVENTHUB_URL,
        'WEBHOOKS_URL_BASE': settings.WEBHOOKS_URL_BASE,
        'DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE': settings.DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE,
        'ALLOW_EVENTHUB': settings.ALLOW_EVENTHUB,
        'DIFFGRAM_INSTALL_FINGERPRINT': settings.DIFFGRAM_INSTALL_FINGERPRINT
    }
    email = {
        'EMAIL_VALIDATION': settings.EMAIL_VALIDATION,
        'MAILGUN_KEY': bool(settings.MAILGUN_KEY),
        'EMAIL_DOMAIN_NAME': settings.EMAIL_DOMAIN_NAME
    }
    storage = {
        'DIFFGRAM_STATIC_STORAGE_PROVIDER': settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
    }

    out['general'] = general
    out['email'] = email
    out['storage'] = storage
    return out
