try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *
from shared.permissions.super_admin_only import Super_Admin
from shared.data_tools_core import Data_tools
import uuid
import tempfile
from shared.database.image import Image
from shared.database.system_configs.system_configs import SystemConfigs

data_tools = Data_tools().data_tools


@routes.route('/api/v1/system/logo', methods = ['GET'])
def api_system_get_logo():
    """
        Open URL to get the system logo.
    :return:
    """

    log = regular_log.default()
    with sessionMaker.session_scope() as session:
        logo_data, log = system_get_logo_core(session = session, log = log)
        if regular_log.log_has_error(log):
            return jsonify(log = log), 400

        return jsonify(logo_data = logo_data)


def system_get_logo_core(session, log = regular_log.default()):
    # Upload to temp dir
    config = SystemConfigs.get_configs(session = session)
    config_data = config.serialize(session = session)
    logo_data = config_data.get('logo')
    return logo_data, log
