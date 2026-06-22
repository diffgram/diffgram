# Import necessary modules and classes.
# An attempt is made to import from the 'methods.regular.regular_api' module.
# If that fails, the 'default.methods.regular.regular_api' module is imported instead.
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

# Import the OAuth2Provider class from the 'shared.auth' package.
from shared.auth.OAuth2Provider import OAuth2Provider

# Define the route for the API endpoint '/api/configs/is-oauth2-set'.
@routes.route('/api/configs/is-oauth2-set')
def oauth2_is_set():
    # Check if OAuth2 is disabled in the settings.
    if settings.USE_OAUTH2 is False:
        # If OAuth2 is disabled, return a JSON object indicating that OAuth2 is not in use.
        return jsonify({"use_oauth2": False})

    # Determine if OAuth2 is set up by checking the following conditions:
    # 1. OAuth2 is enabled in the settings.
    # 2. The OAuth2 provider host is set in the settings.
    # 3. The OAuth2 provider client ID is set in the settings.
    is_set = settings.USE_OAUTH2 and \
             settings.OAUTH2_PROVIDER_HOST and \
             settings.OAUTH2_PROVIDER_CLIENT_ID

    # If all the conditions are met, proceed with OAuth2 setup.
    if is_set:
        # Create an instance of the OAuth2Provider class.
        oauth2 = OAuth2Provider()
        # Get the OAuth2 client object.
        oauth2_client = oauth2.get_client()
        # Get the login URL for the OAuth2 provider.
        login_url = oauth2_client.get_login_url()
        # Return a JSON object indicating that OAuth2 is in use and provide the login URL.
        return jsonify({"use_oauth2": True, "login_url": login_url})

    # If any of the conditions for OAuth2 setup are not met, return a JSON object indicating that OAuth2 is not in use.
    return jsonify({"use_oauth2": False})

