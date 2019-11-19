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
eb_token = os.environ['eb_apikey']


# App vars
location = 'sandiego'
category_id = 103
event_start = 'today'

eb_endpoint = 'https://www.eventbriteapi.com/v3/events/search/' + \
    '?location.address=' + location + \
    '&categories=' + str(category_id) + \
    '&start_date.keyword=' + event_start + \
    '&token=' + eb_token

# Retrieve Hostname
hostname = socket.gethostname()

# Define Flask app name
event = Flask(__name__)

# Fix CORS.


@event.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Create an error handler


@event.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 404}), 404)


def event_fetch():
    # DB setup
    # Connect to the database
    try:
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_pass,
                                     db=db)
        print('Successfully connected to the DB')
    except:
        print('Unable to setup DB connection, skipping')
        return None
    # Fetch Events
    try:
        events_request = requests.get(eb_endpoint)
    except:
        print('An error occurred while connecting to the external service')
        return None

    for event in events_request.json()['events']:
        # Encode in utf-8 to prevent accented characters throwing exceptions
        try:
            event_name = event['name']['html'].encode("utf-8", "strict")
            start_date = event['start']['local']
        except:
            print('Unable to parse response, skipping')
            continue
        try:
            description = event['description']['text'].encode(
                "utf-8", "strict")
        except:
            description = event_name

        try:
            event_id = event['id']
        except:
            print('Can\'t set event_id')
            continue
        try:
            event_url = event['url']
        except:
            print('Can\'t set event_url')
            continue
        try:
            logo_url = event['logo']['url']
        except:
            print('Can\'t set logo_url')
            continue
        try:
            venue_id = event['venue_id']
        except:
            print('Can\'t set venue_id')
            continue

        # Fetch venue details
        venue_endpoint = 'https://www.eventbriteapi.com/v3/venues/' + venue_id + \
            '?token=' + eb_token
        try:
            venue_request = requests.get(venue_endpoint)
            venue_name = venue_request.json()['name']
            venue_address = venue_request.json()['address']['address_1']
            venue_city = venue_request.json()['address']['city']
        except:
            print('Unable to connect to the external service, will try later...')
            return None

        # Create DB records
        try:
            with connection.cursor() as cursor:
                # Check if record exists
                sql = "SELECT * from events WHERE event_id = {}".format(
                    event_id)
                cursor.execute(sql, ())
                if cursor.rowcount == 0:
                    sql = "INSERT INTO `events` (`name`, `start_date`, `venue_name`, `venue_address`, `venue_city`,\
                                `description`, `event_id`, `event_url`, `logo_url`, `venue_id`) \
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (event_name, start_date, venue_name, venue_address,
                                         venue_city, description, event_id, event_url, logo_url, venue_id))
                    connection.commit()
                    cursor.close()
                    print('Successully created DB records for Events')
            connection.close()
        except:
            print('An error occurred while updating records in the DB')
            return None


# Fetch weather for the 1st time
event_fetch()


@event.route('/api/v1/event_fetch', methods=['GET'])
def fetch():
    try:
        event_fetch()
        return make_response(jsonify({'Event fetched and DB updated': 200}), 200)
    except:
        return make_response(jsonify({'Unable to fetch event': 404}), 404)


# Run event fetcher as long as the program is running
if __name__ == '__main__':
    event.run(host='0.0.0.0', port=5002, debug=False)
