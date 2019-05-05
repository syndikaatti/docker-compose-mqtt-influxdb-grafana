#!/usr/bin/python3
from geojson import Point, Feature
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_restful import Resource, Api
import json
import os

app = Flask(__name__)
api = Api(app)
MAPBOX_ACCESS_KEY = os.environ['MAPBOX_ACCESS_KEY']
LOCATIONSPATH = "/tmp/json/parkinglocations.json"

@app.route('/')
def mapbox_js():
    parking_locations = get_parking_locations()
    return render_template(
        'mapbox_js.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY,
        parking_locations=parking_locations)


class ParkingLocations(Resource):
    def get(self):
        with open(LOCATIONSPATH, "r") as json_data:
            locations = json.load()
        return locations

def get_parking_locations():
    parking_locations = []
    with open("/tmp/json/parking_locations.json", "r") as json_data:
        locations = json.load(json_data)
        for location in locations:
            point = Point([location['long'], location['lat']])
            marker_color = "#32CD32"
            if (location['status'] == 0):
                 marker_color = "#FF0000"
            properties = {
                    'title': location['id'],
                    'icon' : 'car',
                    'marker-color': marker_color
            }
            feature = Feature(geometry = point, properties=properties)
            parking_locations.append(feature)
    return parking_locations

# Add all the rest api paths
api.add_resource(ParkingLocations, '/locations')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
