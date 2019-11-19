from flask import Flask, jsonify, abort, make_response
import requests
import json
import pymysql
import time
import os
import socket

# temp vars (need to be environment vars)
 # proxies = {'http': '192.118.78.199:80', 'https': '192.118.78.199:80'}

db_host = os.environ['db_host']
db_user = os.environ['db_user']
db_pass = os.environ['db_pass']
db = os.environ['db_database']
bing_apikey = os.environ['bing_maps_api_key']

# App vars
# location_square = '37.190,-122.550,37.890,-121.670' # SF Bay area
location_square = '32.553,-116.936,32.982,-117.254'  # San Diego
incidents_endpoint = 'http://dev.virtualearth.net/REST/v1/Traffic/Incidents/' + \
    location_square + '?key=' + bing_apikey

# Retrieve Hostname
hostname = socket.gethostname()

# Define Flask app name
incident = Flask(__name__)

# Fix CORS.

@incident.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Create an error handler


@incident.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 404}), 404)

def incident_fetch():
    # DB setup
    # Connect to the database
    try:
        connection = pymysql.connect(host=db_host,
                                    user=db_user,
                                    password=db_pass,
                                    db=db)
        print('Successfully connected to the DB')
    except:
        print('An error occurred while connecting to the database')
        return None

    # Fetch Events
    try:
        incident_request = requests.get(incidents_endpoint)
    except:
        print('An error occurred while connecting to the external service')
        return None

    for incident in incident_request.json()['resourceSets'][0]['resources']:
        # Encode in utf-8 to prevent accented characters throwing exceptions
        try:
            description = incident['description'].encode("utf-8", "strict")
            severity = incident['severity']
            incident_id = incident['incidentId']
            end = incident['end'].split('(')[1].split(')')[0][:-3]
            coordinates = str(incident['point']['coordinates'][0]) + ',' + \
                str(incident['point']['coordinates'][1])
        except:
            print('An error has occurred parsing JSON response, skipping')
            continue

        # Create DB records
        try:
            with connection.cursor() as cursor:
                # Check if record exists
                sql = "SELECT * from incidents WHERE incident_id = {}".format(
                    incident_id)
                cursor.execute(sql, ())
                if cursor.rowcount == 0:
                    sql = "INSERT INTO `incidents` (`description`, `severity`, `incident_id`, `coordinates`, `end`) \
                                VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (description, severity,
                                        incident_id, coordinates, end))
                    connection.commit()
                    cursor.close()
                    print('Successfully created DB records for Incidents')
            connection.close()
        except:
            print('An error occurred while updating records in the DB')
            continue


# Fetch incidents for the 1st time
incident_fetch()

@incident.route('/api/v1/incident_fetch', methods=['GET'])
def fetch():
    try:
        incident_fetch()
        return make_response(jsonify({'Incident fetched and DB updated': 200}), 200)
    except:
        return make_response(jsonify({'Unable to fetch incident': 404}), 404)


# Run incident fetcher as long as the program is running
if __name__ == '__main__':
    incident.run(host='0.0.0.0', port=5003, debug=False)