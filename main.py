import os
import math
import populartimes
import flask
from pytz import timezone
from timezonefinder import TimezoneFinder
from datetime import datetime, date

timezone_finder = TimezoneFinder(in_memory=True)

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
    (latitude, longtitude) = (
        (request.args.get('latitude'), request.args.get('longtitude')) if request.args and 'latitude' in request.args and 'longtitude' in request.args else
        (request_json['latitude'], request_json['longtitude']) if request_json and 'latitude' in request_json and 'longtitude' in request_json else
        (None, None)
    )
    if latitude is None or longtitude is None:
        return flask.jsonify({ 'status': 'FAILURE', 'search_result': [] })

    api_key = os.environ.get('API_KEY', None)
    if api_key is None:
        return flask.jsonify({ 'status': 'FAILURE', 'search_result': [] })

    SEARCHING_RADIUS = 500
    PLACE_TYPES = ['cafe']
    NUMBER_OF_THREADS = 20
    SHOULD_INCLUDE_PLACES_EVEN_WITHOUT_POPULARTIMES = False
    delimiting_points = calulate_delimiliting_points(latitude, longtitude, SEARCHING_RADIUS)
    delimiting_point1 = delimiting_points[0]
    delimiting_point2 = delimiting_points[1]

    search_result = populartimes.get(api_key, PLACE_TYPES, delimiting_point1, delimiting_point2, NUMBER_OF_THREADS, SEARCHING_RADIUS, SHOULD_INCLUDE_PLACES_EVEN_WITHOUT_POPULARTIMES)
    formated_result = format_data(latitude, longtitude, search_result)
    result_json = {
        'status': 'SUCCESS',
        'search_result': formated_result,
        'datetime': datetime.now(), # DEV LOG
        # FIXME: timezone does not work
        'datetime_localized': datetime.now(timezone(timezone_finder.timezone_at(lat=latitude, lng=longtitude))), # DEV LOG
        'zz_row_result': search_result # DEV LOG
    }
    return flask.jsonify(result_json)


def calulate_delimiliting_points(latitude, longtitude, serching_radius):
    PI = math.pi
    EQUATORIAL_RADIUS = 6378136.6
    POLAR_RADIUS = 6356751.9
    latitude_difference = (180 * serching_radius) / (PI * POLAR_RADIUS)
    longtitude_difference = (180 * serching_radius) / (PI * EQUATORIAL_RADIUS * math.cos(latitude))
    southwest_delimiliting_point = (latitude - latitude_difference, longtitude - longtitude_difference)
    northeast_delimiliting_point = (latitude + latitude_difference, longtitude + longtitude_difference)
    return (southwest_delimiliting_point, northeast_delimiliting_point)


def format_data(latitude, longitude, row_data):
    WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    timezone_string = timezone_finder.timezone_at(lat=latitude, lng=longitude)
    # FIXME: timezone does not work
    current_datetime = datetime.now(timezone(timezone_string))
    current_date_integer = datetime(current_datetime.year, current_datetime.month, current_datetime.day).weekday()
    current_hour = current_datetime.hour
    current_date = WEEK[current_date_integer]
    return list(map(lambda x: format_place_data(current_date, current_hour, x), row_data))


def format_place_data(current_date, current_hour, place_data):
    todays_populartimes = list(filter(lambda x: x['name'] == current_date, place_data['populartimes']))[0]
    current_popularity = todays_populartimes['data'][current_hour]
    return {
        'address': place_data['address'],
        'coordinates': place_data['coordinates'],
        'id': place_data['id'],
        'name': place_data['name'],
        'popularity': current_popularity,
        'rating': place_data['rating']
    }