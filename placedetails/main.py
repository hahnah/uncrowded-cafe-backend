import os
import requests
import flask


def place_details(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    place_id = (
        request.args.get('place_id') if request.args and 'place_id' in request.args else
        request_json['place_id'] if request_json and 'place_id' in request_json else
        None
    )
    if place_id is None:
        return flask.jsonify({ 'status': 'FAILURE', 'search_result': [] })

    api_key = os.environ.get('API_KEY', None)
    if api_key is None:
        return flask.jsonify({ 'status': 'FAILURE', 'search_result': [] })

    BASE_URL = 'https://maps.googleapis.com/maps/api/place/'
    DETAIL_URL = BASE_URL + 'details/json?placeid={}&fields=opening_hours,photos&key={}'
    request_url = DETAIL_URL.format(place_id, api_key)

    response = requests.get(request_url).json()['result']
    open_now = response['opening_hours']['open_now']
    photo_reference = response['photos'][0]['photo_reference']

    result_json = {
        'status': 'SUCCESS',
        'result': {
            'open_now': open_now,
            'photo_reference': photo_reference
        }
    }
    return flask.jsonify(result_json)