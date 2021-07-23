from flask import current_app
from flask import jsonify
from shared.settings import settings
import traceback


@current_app.errorhandler(Exception)
def handle_exception(e):
    payload = {'error': str(e)}
    if settings.DIFFGRAM_ERROR_SEND_TRACES_IN_RESPONSE:
        payload['trace'] = traceback.format_exc()
    return jsonify(payload), 500
