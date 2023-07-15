try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.permissions.super_admin_only import Super_Admin


@routes.route('/api/v1/admin/install/info',
              methods = ['GET'])
@Super_Admin.is_super(allow_support=True)
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
        'IS_OPEN_SOURCE': settings.IS_OPEN_SOURCE,
        'URL_BASE': settings.URL_BASE,
        'RUNNING_LOCALLY': settings.RUNNING_LOCALLY,
        'DATABASE_URL': bool(settings.DATABASE_URL),
        'DATABASE_CONNECTION_POOL_SIZE': settings.DATABASE_CONNECTION_POOL_SIZE,
        'WALRUS_SERVICE_URL_BASE': settings.WALRUS_SERVICE_URL_BASE,
        'EVENTHUB_URL': settings.EVENTHUB_URL,
        'WEBHOOKS_URL_BASE': settings.WEBHOOKS_URL_BASE,
        'DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE': settings.DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE,
        'ALLOW_EVENTHUB': settings.ALLOW_EVENTHUB,
        'DIFFGRAM_INSTALL_FINGERPRINT': settings.DIFFGRAM_INSTALL_FINGERPRINT,
        'PROCESS_MEDIA_REMOTE_QUEUE_ON': settings.PROCESS_MEDIA_REMOTE_QUEUE_ON,
        'PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY': settings.PROCESS_MEDIA_ENQUEUE_LOCALLY_IMMEDIATELY,
        'DIFFGRAM_MINIO_DISABLED_SSL_VERIFY': settings.DIFFGRAM_MINIO_DISABLED_SSL_VERIFY,
        'SIGNED_URL_CACHE_MINIMUM_SECONDS_VALID': settings.SIGNED_URL_CACHE_MINIMUM_SECONDS_VALID,

    }
    oauth2 = {
        'USE_OAUTH2': settings.USE_OAUTH2,
        'OAUTH2_PROVIDER_NAME': settings.OAUTH2_PROVIDER_NAME,
        'OAUTH2_PROVIDER_HOST': settings.OAUTH2_PROVIDER_HOST,
        'OAUTH2_PROVIDER_CLIENT_ID': settings.OAUTH2_PROVIDER_CLIENT_ID,
        'OAUTH2_PROVIDER_CLIENT_SECRET': bool(settings.OAUTH2_PROVIDER_CLIENT_SECRET),
        'OAUTH2_PROVIDER_PUBLIC_KEY': settings.OAUTH2_PROVIDER_PUBLIC_KEY,
        'COGNITO_LOGIN_URL': settings.COGNITO_LOGIN_URL,
    }

    rabbitmq = {
        'RABBITMQ_DEFAULT_USER': settings.RABBITMQ_DEFAULT_USER,
        'RABBITMQ_HOST': settings.RABBITMQ_HOST,
        'USE_RABBIT_MQ': settings.USE_RABBIT_MQ,
        'RABBITMQ_PORT': settings.RABBITMQ_PORT,
    }
    email = {
        'EMAIL_VALIDATION': settings.EMAIL_VALIDATION,
        'MAILGUN_KEY': bool(settings.MAILGUN_KEY),
        'EMAIL_DOMAIN_NAME': settings.EMAIL_DOMAIN_NAME,
        'EMAIL_REPLY_TO': settings.EMAIL_REPLY_TO
    }
    storage = {
        'DIFFGRAM_STATIC_STORAGE_PROVIDER': settings.DIFFGRAM_STATIC_STORAGE_PROVIDER,
    }

    out['general'] = general
    out['email'] = email
    out['storage'] = storage
    out['oauth2'] = oauth2
    out['rabbitmq'] = rabbitmq
    return out
