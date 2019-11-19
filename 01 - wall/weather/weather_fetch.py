from flask import Flask, jsonify, abort, make_response
import requests
import json
import pymysql
import time
import os
import socket

# Variables
# proxies = {'http': '192.118.78.199:80', 'https': '192.118.78.199:80'}

db_host = os.environ['db_host']
db_user = os.environ['db_user']
db_pass = os.environ['db_pass']
db = os.environ['db_database']
ow_apikey = os.environ['ow_apikey']

# city_id = '5392171' # San Jose, CA
zipCode = '92101,us'  # San Diego, CA
units = 'imperial'  # metric or imperial

weather_endpoint = 'https://api.openweathermap.org/data/2.5/weather?zip=' + zipCode + \
    '&units=' + units + '&appid=' + ow_apikey

# Retrieve Hostname
hostname = socket.gethostname()

# Define Flask app name
weather = Flask(__name__)

# Fix CORS.

@weather.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Create an error handler

@weather.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 404}), 404)


def weather_fetch():
    # DB setup
    # Connect to the database
    try:
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     passwd=db_pass,
                                     db=db)
        print('Successfully connected to the DB')
    except:
        print('Unable to setup DB connection, skipping')
        return None

    # Fetch Weather
    try:
        weather_request = requests.get(weather_endpoint)
        weather_json = json.loads(weather_request.content)

        description = weather_json['weather'][0]['description']
        icon = weather_json['weather'][0]['icon']
        temp = weather_json['main']['temp']
        temp_min = weather_json['main']['temp_min']
        temp_max = weather_json['main']['temp_max']
        timestamp = weather_json['dt']
        humidity = weather_json['main']['humidity']
        city = weather_json['name']
    except:
        print('An error occurred while connecting to the external service')
        return None

    # Create DB records
    try:
        with connection.cursor() as cursor:
            # Check if record exists
            sql = "SELECT * from weather WHERE timestamp = {}".format(
                timestamp)
            cursor.execute(sql, ())
            if cursor.rowcount == 0:
                sql = "INSERT INTO `weather` (`description`, `icon`, `temp`, `temp_min`, \
                            `temp_max`, `timestamp`, `humidity`, `city`) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (description, icon,
                                     temp, temp_min, temp_max, timestamp, humidity, city))
                connection.commit()
                print('Successfully created DB record for weather info')
                cursor.close()
        connection.close()
    except:
        print('An error occurred while updating records in the DB')
        return None


# Fetch weather for the 1st time
weather_fetch()


@weather.route('/api/v1/weather_fetch', methods=['GET'])
def fetch():
    try:
        weather_fetch()
        return make_response(jsonify({'Weather fetched and DB updated': 200}), 200)
    except:
        return make_response(jsonify({'Unable to fetch weather': 404}), 404)


# Run weather fetcher as long as the program is running
if __name__ == '__main__':
    weather.run(host='0.0.0.0', port=5001, debug=False)

