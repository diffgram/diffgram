try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *


@routes.route('/api/configs/is-open-source')
def api_is_open_source():
    is_open_source = settings.IS_OPEN_SOURCE

    if is_open_source:
        return jsonify({"is_open_source": True})
    return jsonify({"is_open_source": False})
