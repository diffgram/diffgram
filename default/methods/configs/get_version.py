try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *


@routes.route('/api/configs/version')
def api_get_version():
    version = settings.DIFFGRAM_VERSION_TAG

    return jsonify({"version": version})
