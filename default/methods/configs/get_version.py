try:
    # Import the regular API from the methods.regular.regular_api module,
    # or use the default implementation if there is an exception.
    from methods.regular.regular_api import *
except:
    # Import the regular API from the default.methods.regular.regular_api module.
    from default.methods.regular.regular_api import *


# Define a new route for the Flask application at the URL '/api/configs/version'
# that returns the version of the Diffgram API as a JSON response.
@routes.route('/api/configs/version')
def api_get_version():
    # Get the version of the Diffgram API from the settings module.
    version = settings.DIFFGRAM_VERSION_TAG

    # Return a JSON response with the version number.
    return jsonify({"version": version})
