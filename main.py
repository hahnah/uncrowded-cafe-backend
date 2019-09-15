import os
import populartimes
import flask

def popular_times(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    api_key = os.environ.get('API_KEY', 'Specified environment variable is not set.')
    if request.args and 'place_id' in request.args:
	    return flask.jsonify(populartimes.get_id(api_key, request.args.get('place_id')))
    elif request_json and 'place_id' in request_json:
        return flask.jsonify(populartimes.get_id(api_key, request_json['place_id']))
    else:
        return flask.jsonify({})