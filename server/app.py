#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

# GET /campers
# Return JSON data in the format below. Note: you should return a JSON response in this format, without any additional nested data related to each camper.
@app.route('/campers', methods=['GET', 'POST'])
def campers():
    if request.method == 'GET':
        return [camper.to_dict() for camper in Camper.query.all()]

# POST /campers
# Return JSON data in the format below. Note: you should return a JSON response in this format, without any additional nested data related to each camper.    
# If the Camper is created successfully, send back a response with the new Camper
# If the Camper is not created successfully, return the following JSON data, along with the appropriate HTTP status code:    
    elif request.method == 'POST':
        data = request.get_json()

        try:
            camper = Camper(name=data.get('name'), age = data.get('age'))
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict()
        except ValueError:
            return{'error': '400: Validation Error'}, 400

# GET /campers/int:id
# If the Camper exists, return JSON data in the format below. Note: you will need to serialize the data for this response differently than for the GET /campers route. Make sure to include an array of activities for each camper.        
@app.route('/campers/<int:id>', methods=['GET'])
def camper_by_id(id):
    camper = Camper.query.filter_by(id=id).first()

    if camper:
        return camper.to_dict()
    return {"error": "404: Camper not found"}, 404

# GET /activities
# Return JSON data
@app.route('/activities', methods=['GET'])
def activities():
    #because using to_dict, create serializer rules in models.py
    return [activity.to_dict() for activity in Activity.query.all()]

# DELETE /activities/int:id
# If the Activity exists, it should be removed from the database, along with any Signups that are associated with it (a Signup belongs to an Activity, so you need to delete the Signups before the Activity can be deleted).
# After deleting the Activity, return an empty response body, along with the appropriate HTTP status code.
# If the Activity does not exist, return the following JSON data, along with the appropriate HTTP status code:
@app.route('/activities/<int:id>', methods=['DELETE'])
def activity_by_id(id):
    activity = Activity.query.filter_by(id=id).first()

    if activity:
        db.session.delete(activity)
        db.session.commit()
        return{}, 204
    return{"error": "404: Activity not found"}, 404

# POST /signups
# This route should create a new Signup that is associated with an existing Camper and Activity. It should accept an object with the following properties in the body of the request:
# If the Signup is created successfully, send back a response with the data related to the Activity:
# If the Signup is not created successfully, return the following JSON data, along with the appropriate HTTP status code:
@app.route('/signups', methods=['POST'])
def signups():
    data = request.get_json()

    try:
        signup = Signup(
            time = data.get('time'),
            camper_id = data.get('camper_id'),
            activity_id = data.get('activity_id')
        )
        db.session.add(signup)
        db.session.commit()
        return signup.to_dict()
    except ValueError:
        return {"error": "400: Validation Error"}, 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
