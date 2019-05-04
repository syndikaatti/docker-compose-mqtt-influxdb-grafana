#!/usr/bin/python3
from geojson import Point, Feature
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import json
import os

app = Flask(__name__)
#app.config.from_object(__name__)
#app.config.from_envvar('APP_CONFIG_FILE', silent=True)
#MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']
MAPBOX_ACCESS_KEY = os.environ['MAPBOX_ACCESS_KEY']

@app.route('/')
def mapbox_js():
    parking_locations = get_parking_locations()
    return render_template(
        'mapbox_js.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY,
        parking_locations=parking_locations)

def get_parking_locations():
    parking_locations = []
    with open("../parking_locations.json", "r") as json_data:
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

# Read data from the database and returns a dict?
def read_parking_data():
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
