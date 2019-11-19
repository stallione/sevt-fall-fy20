from flask import Flask, jsonify, abort, make_response
import requests
import json
import pymysql
import datetime
import time
import random
import socket
import os

# temp vars (need to be environment vars)
# proxies = {'http': '192.118.78.199:80', 'https': '192.118.78.199:80'}

db_host = os.environ['db_host']
db_user = os.environ['db_user']
db_pass = os.environ['db_pass']
db = os.environ['db_database']

# Iterate through environment variables and guess the right services endpoints
# Addresses Cloudcenter behavior where service names are appended with a random string
# IMPORTANT: You cannot run multiple Tarantulas in the same namespace


def set_service_endpoint(servicename, servicetype):  # Servicetype: PORT, HOST
    servicename = servicename.upper().replace('-', '_')
    if servicetype == 'PORT':
        for var in os.environ:
            if servicename in var:
                if 'SERVICE_PORT' in var:
                    return os.environ[var]
    elif servicetype == 'HOST':
        for var in os.environ:
            if servicename in var:
                if 'SERVICE_HOST' in var:
                    return os.environ[var]
    else:
        return 'Invalid servicetype (valid: PORT, HOST)'


weather_endpoint = '{}:{}'.format(set_service_endpoint(
    'weather', 'HOST'), set_service_endpoint('weather', 'PORT'))
event_endpoint = '{}:{}'.format(set_service_endpoint(
    'event', 'HOST'), set_service_endpoint('event', 'PORT'))
incident_endpoint = '{}:{}'.format(set_service_endpoint(
    'incident', 'HOST'), set_service_endpoint('incident', 'PORT'))

if (weather_endpoint == 'None:None') or (event_endpoint == 'None:None') or (incident_endpoint == 'None:None'):
    print('error', 'Unable to set endpoints. The apiserver will always yield a 404. Is the app running inside Kubernetes? '
          'In order to work, apiserver MUST be started AFTER weather, event and incident fetchers')


# Request to fetchers

def request_fetch(service):
    if service == 'weather':
        try:
            requests.get(
                'http://{}/api/v1/weather_fetch'.format(weather_endpoint))
        except:
            return 'Unable to reach {} service'.format('service')
    elif service == 'event':
        try:
            requests.get('http://{}/api/v1/event_fetch'.format(event_endpoint))
        except:
            return 'Unable to reach {} service'.format('service')
    elif service == 'incident':
        try:
            requests.get(
                'http://{}/api/v1/incident_fetch'.format(incident_endpoint))
        except:
            return 'Unable to reach {} service'.format('service')
    else:
        return 'Unsupported/Unknown Service'


# Retrieve Hostname
hostname = socket.gethostname()

# Define Flask app name
apiserver = Flask(__name__)

# Fix CORS.


@apiserver.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Create an error handler


@apiserver.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 404}), 404)


@apiserver.route('/api/v1/services', methods=['GET'])
def services():

    # DB setup
    # Connect to the database
    try:
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_pass,
                                     db=db)
        print('Successfully connected to the DB')
    except:
        return 'Unable to connect to the DB'

    # Build DB Queries

    weather_query = """select description, icon, temp, temp_min, \
    temp_max, humidity, city from weather order by timestamp DESC"""

    event_query = """select name, start_date, venue_name, \
    venue_address, venue_city, description, event_url, \
    logo_url from events where start_date like %s"""

    incident_query = """select severity, coordinates, description \
    from incidents where end > %s"""

    # Fetch data from DB
    try:
        with connection.cursor() as weather_cursor:
            weather_cursor.execute(weather_query, ())

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        with connection.cursor() as event_cursor:
            event_cursor.execute(event_query, (today + '%'))

        with connection.cursor() as incident_cursor:
            # Exclude expired entries
            incident_cursor.execute(incident_query, (int(time.time())))
    except:
        return 'Something\'s wrong. Unable to fetch data from the DB, check whether the services are updating records'

    try:
        # Extract Weather Column names
        weather_row_headers = [x[0] for x in weather_cursor.description]
        # Extracting Event content and convert to list of dictionary
        weather_content = weather_cursor.fetchall()
        weather_report = []
        for result in weather_content:
            weather_report.append(dict(zip(weather_row_headers, result)))
        print('Successfully parsed Weather DB record and created dictionary')
    except:
        return 'Unable to parse Weather DB record'

    try:
        # Extract Event Column names
        event_row_headers = [x[0] for x in event_cursor.description]
        # Extracting Event content and convert to list of dictionary
        event_content = event_cursor.fetchall()
        event_list = []
        for result in event_content:
            event_list.append(dict(zip(event_row_headers, result)))
        print('Successfully parsed Event DB record and created dictionary')
    except:
        return 'Unable to parse Event DB record'

    try:
        # Extract Incident Column names
        incident_row_headers = [x[0] for x in incident_cursor.description]
        # Extracting Incident content and convert to list of dictionary
        incident_content = incident_cursor.fetchall()
        incident_list = []
        for result in incident_content:
            incident_list.append(dict(zip(incident_row_headers, result)))
        print('Successfully parsed Incident DB record and created dictionary')
    except:
        return 'Unable to parse Incident DB record'

    # Pick a random event
    try:
        random_event = random.choice(event_list)
    except:
        random_event = {
            "content": "Not available. Unable to find events in the DB"
        }
    # Pick a random incident
    try:
        random_incident = random.choice(incident_list)
    except:
        random_incident = {
            "content": "Not available. Unable to find incidents in the DB"
        }

    # Create aggregated JSON response
    try:
        payload = {}
        payload['weather'] = {}
        payload['event'] = {}
        payload['incident'] = {}
        payload['appspecs'] = {
            "app_version": "0.1",
            "serving_hostname": hostname
        }
    except:
        return 'Unable to create aggregated JSON response'

    # Weather (we only need the 1st record as the most recent update)
    try:
        for key in weather_report[0]:
            payload['weather'][key] = weather_report[0][key]
    except:
        payload['weather'] = {
            "content": "Not available. Unable to find weather info in the DB"
        }

    # Events
    for key in random_event:
        try:
            payload['event'][key] = random_event[key].decode(
                'utf-8')  # or ISO-8859-1
        except:
            payload['event'][key] = random_event[key]

    # Incidents
    for key in random_incident:
        payload['incident'][key] = random_incident[key]

    # Returns and exception if unable to convert dict to JSON
    try:
        payload_json = json.dumps(payload)
        return(payload_json)
    except:
        print(payload)
        return "Exception occurred. Check Encoding"
    finally:
        if random.randint(1, 10) > 8:
            # Request content update 20% of the time
            request_fetch('weather')
            request_fetch('event')
            request_fetch('incident')
            print('Requested external service update')


# Run API server as long as the program is running
if __name__ == '__main__':
    apiserver.run(host='0.0.0.0', debug=False)