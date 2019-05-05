#!/usr/bin/python3
from geojson import Point, Feature
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_restful import Resource, Api
import json
import os

app = Flask(__name__)
api = Api(app)
MAPBOX_ACCESS_KEY = os.environ['MAPBOX_ACCESS_KEY']
LOCATIONSPATH = "/tmp/json/parking_locations.json"

@app.route('/')
def mapbox_js():
    parking_locations = get_parking_locations()
    return render_template(
        'mapbox_js.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY,
        parking_locations=parking_locations)


class ParkingLocations(Resource):
    def get(self):
        return get_data_json(LOCATIONSPATH)

class SingleParkingLocation(Resource):
    def get(self, location_id):
        locations = get_data_json(LOCATIONSPATH)
        for location in locations:
            if location['id'] == location_id:
                return location
        return "Data point not found", 404

class FreeParkingLocations(Resource):
    def get(self):
        locations = get_data_json(LOCATIONSPATH)
        free = []
        for location in locations:
            if location['status'] == 0:
                free.append(location)
        if len(locations) == 0:
            return "No free parking locations found :("
        return free

class MapParkingLocations(Resource):
    def get(self):
        return get_parking_locations()

def get_data_json(path):
    with open(path, "r") as json_data:
        locations = json.load(json_data)
    return locations

def get_parking_locations():
    parking_locations = []
    locations = get_data_json(LOCATIONSPATH)
    for location in locations:
        point = Point([location['long'], location['lat']])
        marker_color = "#32CD32"
        marker_symbol = 'parking'
        if (location['status'] == 1):
             marker_color = "#FF0000"
             marker_symbol = 'car'
        properties = {
                'title': location['id'],
                'marker-symbol': marker_symbol,
                'marker-color': marker_color
        }
        feature = Feature(geometry = point, properties=properties)
        parking_locations.append(feature)
    return parking_locations

# Add all the rest api paths
api.add_resource(ParkingLocations, '/locations')
api.add_resource(SingleParkingLocation, '/location/<int:location_id>')
api.add_resource(FreeParkingLocations, '/locations/free')
api.add_resource(MapParkingLocations, '/maplocations')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
