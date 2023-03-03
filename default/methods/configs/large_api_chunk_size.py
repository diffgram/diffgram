try:
    from methods.regular.regular_api import *
except:
    from default.methods.regular.regular_api import *

@routes.route('/api/configs/large-api-chunk-size')
def large_api_chunk_size():
    return jsonify({"large_api_chunk_size": settings.LARGE_API_CHUNK_SIZE})
