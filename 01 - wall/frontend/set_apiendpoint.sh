#!/bin/bash
# Get K8S token and understand what is the API Server Service


# Set the right Bing API Key
sed -i "s/bing_maps_api_key/$bing_maps_api_key/g" js/tarantula.js

# Set the correct apiserver coordinates to make NGINX reverse proxy work
sed -i "s/APISERVERSVC/$LIVEWALL_SILENCE_SERVICE_HOST/g" default.conf
cp -p default.conf /etc/nginx/conf.d/default.conf