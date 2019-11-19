/*

    tarantula.js

    */

"use strict";

// Perform on page load
$(window).on("load", function() {
  console.log("Page loaded");
  // Enable Popovers
  $(function() {
    $('[data-toggle="popover"]').popover();
  });
  tarantulaStatus();
});

var callAPIServerEvery = 10000;

// Perform every 2 seconds
setInterval(function() {
  tarantulaStatus();
}, callAPIServerEvery);

// Set content type to JSON for POST calls
$.ajaxSetup({
  contentType: "application/json; charset=utf-8"
});

// Set variable to point to the right API server
var apiserverEndpointHost = location.hostname;

// Set vars
var apiserver_hostname = $("#id-row-1-col-2");
var apiserver_version = $("#id-row-1-col-3");

var fool_hostname = $("#id-row-2-col-2");
var fool_version = $("#id-row-2-col-3");
var fool_payload = $("#id-row-2-col-4");

var rainbow_hostname = $("#id-row-3-col-2");
var rainbow_version = $("#id-row-3-col-3");
var rainbow_payload = $("#id-row-3-col-4");

var stairway_hostname = $("#id-row-4-col-2");
var stairway_version = $("#id-row-4-col-3");
var stairway_payload = $("#id-row-4-col-4");

var modalWeatherBody = $("#id-modal-weather-body");
var modalEventsBody = $("#id-modal-events-body");
var modalTrafficBody = $("#id-modal-traffic-body");

// Set API endpoints
var serviceAPI = "http://" + apiserverEndpointHost + "/api/v1/services";
var bingPicsAPI;
var bingMapCoord;
var bingMapAPI = "bing_maps_api_key";

// Ext references variables
var iconsBaseURL = "./img/w-icons/";

// Capitalize function
function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

// Update Tarantula Status
function tarantulaStatus() {
  console.log("fetching results from apiserver...");
  $.getJSON(serviceAPI)
    .done(function(result) {
      // API Server Update

      $("#id-apiserver-container").html(
        '<b>Serving API Server: </b> <span class="badge badge-secondary">' +
          result.appspecs.serving_hostname +
          "</span>"
      );
      $("#id-apiserver-version").html(
        '<b>API Server Version: </b> <span class="badge badge-pill badge-success">' +
          result.appspecs.app_version +
          "</span>"
      );

      // Weather Service API update

      $("#id-weather-text").html(
        capitalizeFirstLetter(result.weather.description) +
          " in " +
          result.weather.city +
          ". " +
          '<img src="' +
          iconsBaseURL +
          result.weather.icon +
          '.png">' +
          " <br> The temperature is currently <b>" +
          result.weather.temp +
          "</b>°F, humidity level is at <b>" +
          result.weather.humidity +
          "%</b><br><br><b>Min Temp: </b>" +
          result.weather.temp_min +
          "°F<br> <b>Max Temp: </b>" +
          result.weather.temp_max +
          "°F"
      );
      $("#id-weather-container").html(
        '<b>Fetched by Pod: </b> <span class="badge badge-secondary">' +
          result.appspecs.serving_hostname +
          "</span>"
      );
      $("#id-weather-version").html(
        '<b>Pod App Version: </b> <span class="badge badge-pill badge-success">' +
          result.appspecs.app_version +
          "</span>"
      );

      modalWeatherBody.text(JSON.stringify(result.weather, undefined, "\t"));

      // Event Service API update

      $("#id-events-card").attr("src", result.event.logo_url);
      $("#id-events-text").html(
        "<b>Event: </b>" +
          result.event.name +
          "<br>" +
          "<br><b>When: </b>" +
          result.event.start_date.split("T")[0] +
          " at " +
          result.event.start_date.split("T")[1] +
          "<br><br><b>Venue: </b>" +
          result.event.venue_name +
          " - " +
          result.event.venue_address +
          "<br>" +
          result.event.venue_city
      );

      $("#id-event-full-description").attr(
        "data-content",
        result.event.description
      );

      $("#id-events-container").html(
        '<b>Fetched by Pod: </b> <span class="badge badge-secondary">' +
          result.appspecs.serving_hostname +
          "</span>"
      );
      $("#id-events-version").html(
        '<b>Pod App Version: </b> <span class="badge badge-pill badge-success">' +
          result.appspecs.app_version +
          "</span>"
      );

      modalEventsBody.text(JSON.stringify(result.event, undefined, "\t"));

      // Traffic Service API update

      var incidentSeverity;
      if (result.incident.severity == 1) {
        incidentSeverity =
          '<div class="alert alert-danger" role="alert">Critical (Severity 1)</div>';
      } else if (result.incident.severity == 2) {
        incidentSeverity =
          '<div class="alert alert-warning" role="alert">Significant (Severity 2)</div>';
      } else if (result.incident.severity == 3) {
        incidentSeverity =
          '<div class="alert alert-success" role="alert">Normal (Severity 3)</div>';
      } else {
        incidentSeverity =
          '<div class="alert alert-info" role="alert">Low (Severity ' +
          result.incident.severity +
          ")</div>";
      }
      $("#id-traffic-text").html(
        "<b>Report: </b>" +
          result.incident.description +
          "<br><br><b>Severity: </b>" +
          incidentSeverity
      );

      // Build map coordinates
      bingMapCoord = result.incident.coordinates;

      // Call Bing Map service for PNG download
      bingPicsAPI =
        "https://dev.virtualearth.net/REST/v1/Imagery/Map/Road/" +
        bingMapCoord +
        "/15?mapSize=400,200&pp=" +
        bingMapCoord +
        ";21;&pp=" +
        bingMapCoord +
        ";;&pp=" +
        bingMapCoord +
        ";22&ml=TrafficFlow&key=" +
        bingMapAPI;

      // Replace image with current incident map
      $("#id-traffic-card").attr("src", bingPicsAPI);

      $("#id-traffic-container").html(
        '<b>Served by: </b> <span class="badge badge-secondary">' +
          result.appspecs.serving_hostname +
          "</span>"
      );
      $("#id-traffic-version").html(
        '<b>App Version: </b> <span class="badge badge-pill badge-success">' +
          result.appspecs.app_version +
          "</span>"
      );

      modalTrafficBody.text(JSON.stringify(result.incident, undefined, "\t"));

      $("#api-loading").hide(500);
    })
    .fail(function() {
      $("#api-loading").show(500);
      console.log("Unable to call live wall API!");
    });
}
