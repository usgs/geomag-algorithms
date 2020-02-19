from datetime import datetime
from flask import Blueprint, Flask, jsonify, render_template, request, Response
from obspy import UTCDateTime

from geomagio.edge import EdgeFactory
from geomagio.iaga2002 import IAGA2002Writer
from geomagio.imfjson import IMFJSONWriter

blueprint = Blueprint('data', __name__)


def init_app(app: Flask):
    global blueprint

    app.register_blueprint(blueprint)


@blueprint.route('/data', methods=['GET'])
def get_data():
    query_params = request.args

    url = request.url

    if not query_params:

        return render_template('usage.html')

    query = parse_query(query_params)

    timeseries = get_timeseries(query)

    return format_timeseries(timeseries, query)


def parse_query(query):
    """Parse request arguments into a set of parameters

    Parameters
    ----------
    query: Immutable Dict
        request.args object

    Returns
    -------
    params: dictionary
        query parameters dictionary

    Raises
    ------
    WebServiceException
        if any parameters are not supported.
    """
    params = {}

    # Get end time
    if not query.get('endtime'):
        now = datetime.now()
        today = UTCDateTime(
                    now.year,
                    now.month,
                    now.day,
                    0)
        end_time = today
        params['End Time'] = end_time
    else:
        params['End Time'] = UTCDateTime(query.get('endtime'))

    # Get start time
    if not query.get('starttime'):
        start_time = UTCDateTime(params['End Time']) - (24 * 60 * 60 - 1)
        params['Start Time'] = UTCDateTime(start_time)
    else:
        params['Start Time'] = UTCDateTime(query.get('starttime'))

    # Get sampling period
    params['Sampling Period'] = query.get('sampling_period')

    if params['Sampling Period'] == '1':
        params['Sampling Period'] = 'second'

    if params['Sampling Period'] == '60':
        params['Sampling Period'] = 'minute'

    # Get format
    if query.get('format'):
        params['Format'] = query.get('format')
    else:
        params['Format'] = 'iaga2002'

    # Get observatory
    params['Observatory'] = query.get('observatory')

    # Get channels
    channels = query.get('channels').split(',')
    params['Channels'] = channels

    # Get data type
    params['Type'] = query.get('type')

    validate_parameters(params)

    return params


def validate_parameters(params):
    """Verify that parameters are valid.

    Parameters
    ----------
    params: dict
        dictionary of parsed query parameters

    Raises
    ------
    WebServiceException
        if any parameters are not supported.
    """
    valid_data_types = ['variation', 'adjusted',
        'quasi-definitive', 'definitive']
    valid_formats = ['iaga2002', 'json']
    valid_sampling_periods = ['second', 'minute']

    if len(params['Channels']) > 4 and params['Format'] == 'iaga2002':
        raise WebServiceException(
            'No more than four elements allowed for Iaga2002 format.')

    if params['Start Time'] > params['End Time']:
        raise WebServiceException('Start time must be before end time.')

    if params['Type'] not in valid_data_types:
        raise WebServiceException('Bad data type: ' + params['Type'] +
        '. Valid values are: ' + ', '.join(valid_data_types) + '.')

    if params['Sampling Period'] not in valid_sampling_periods:
        raise WebServiceException('Bad sampling_period value: ' + params['Sampling Period'] +
        '. Valid values are: 1, 60.')

    if params['Format'] not in valid_formats:
        raise WebServiceException('Bad format value: ' + params['Format'] +
        '. Valid values are: ' + ', '.join(valid_formats))


def get_timeseries(query):
    """
    Parameters
    ----------
    query: dict
        dictionary of parsed query parameters

    Returns
    -------
    obspy.core.Stream
        timeseries object with requested data
    """
    factory = EdgeFactory()

    timeseries = factory.get_timeseries(
            query['Start Time'], query['End Time'], query['Observatory'], query['Channels'],
            query['Type'], query['Sampling Period'])

    return timeseries


def format_timeseries(timeseries, query):
    """Formats timeseries into JSON or IAGA data

    Parameters
    ----------
    obspy.core.Stream
        timeseries object with requested data

    query: dict
        dictionary of parsed query parameters

    Returns
    -------
    unicode
        IAGA2002 or JSON formatted string.
    """
    if query['Format'] == 'json':
        json_output = IMFJSONWriter.format(timeseries, query['Channels'])

        return json_output

    else:
        iaga_output = IAGA2002Writer.format(timeseries, query['Channels'])

        iaga_output = Response(iaga_output, mimetype="text / plain")

        return iaga_output


class WebServiceException(Exception):
    """Base class for exceptions thrown by web services."""
    pass
