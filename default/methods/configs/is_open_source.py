try:
    from methods.regular import get_is_open_source
except:
    from default.methods.regular import get_is_open_source

@routes.route('/api/configs/is-open-source')
def api_is_open_source() -> Response:
    """
    Returns whether the application is open source or not.
    """
    is_open_source = get_is_open_source()

    if not isinstance(is_open_source, bool):
        return jsonify({"error": "Invalid value for IS_OPEN_SOURCE"}), 400

    return jsonify({"is_open_source": is_open_source})
