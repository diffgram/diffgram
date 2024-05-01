# This module contains functions and configurations related to the large API chunk size.

# Try to import the regular_api module from the methods.regular package. If that fails,
# import it from the default.methods.regular package instead.
try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

# A Flask route that returns the large_api_chunk_size configuration setting as a JSON object.
@routes.route('/api/configs/large-api-chunk-size')
def large_api_chunk_size():
    # Return a JSON object with the large_api_chunk_size setting.
    return jsonify({"large_api_chunk_size": settings.LARGE_API_CHUNK_SIZE})
