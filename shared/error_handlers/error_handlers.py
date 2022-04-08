from flask import current_app
from flask import jsonify
from shared.settings import settings
import traceback
from shared.shared_logger import get_shared_logger
from werkzeug.exceptions import Forbidden, NotFound

logger = get_shared_logger()


@current_app.errorhandler(NotFound)
def handle_exception(e):
    payload = {'error': str(e)}
    return jsonify(payload), 404


@current_app.errorhandler(Exception)
def handle_exception(e):
    payload = {'error': str(e)}
    exc_traceback = traceback.format_exc()
    if settings.DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE:
        payload['trace'] = exc_traceback
    logger.error(exc_traceback)
    try:
        error_code = e.code
    except:
        error_code = 500
    return jsonify(payload), error_code


@current_app.errorhandler(Forbidden)
def handle_forbidden(e):
    payload = {'error': str(e)}
    exc_traceback = traceback.format_exc()
    if settings.DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE:
        payload['trace'] = exc_traceback
    logger.error(exc_traceback)
    return jsonify(payload), 403
