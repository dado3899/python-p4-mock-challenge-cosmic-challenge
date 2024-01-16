#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods = ['GET','POST'])
def scientist_route():
    if request.method == "GET":
        all_scientists = Scientist.query.all()
        dict_scientists = []
        for scientist in all_scientists:
            dict_scientists.append(scientist.to_dict(rules=('-missions',)))
        return make_response(dict_scientists,200)
    elif request.method == "POST":
        try:
            data = request.get_json()
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(rules=('-missions',)),201)
        except:
            return make_response({"errors": ["validation errors"]},400)

@app.route('/scientists/<int:id>', methods = ['GET','PATCH','DELETE'])
def one_scientist_route(id):
    found_scientist = Scientist.query.filter(Scientist.id==id).first()
    if found_scientist:
        if request.method == "GET":
            return make_response(found_scientist.to_dict(),200)
        elif request.method == "PATCH":
            try:
                data = request.get_json()
                for attr in data:
                    setattr(found_scientist,attr,data[attr])
                db.session.add(found_scientist)
                db.session.commit()
                return make_response(found_scientist.to_dict(rules=('-missions',)),202)
            except:
                return make_response({"errors": ["validation errors"]},400)
        elif request.method == "DELETE":
            # missions_to_delete = Mission.query.filter(Mission.scientist_id == found_scientist.id).all()
            db.session.delete(found_scientist)
            db.session.commit()
            return make_response({},204)
    else:
        return make_response({"error": "Scientist not found"},404)


@app.route('/planets', methods=["GET"])
def planets_route():
    if request.method == "GET":
        all_planets = Planet.query.all()
        dict_planets = []
        for planet in all_planets:
            dict_planets.append(planet.to_dict(rules=('-missions',)))
        # [planet.to_dict() for planet in all_planets]
        return make_response(dict_planets,200)
    
@app.route('/missions', methods=["POST"])
def missions_route():
    if request.method == "POST":
        try:
            data = request.get_json()
            new_mission = Mission(
                name = data['name'],
                scientist_id =  data['scientist_id'],
                planet_id = data['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(),201)
        except:
            return make_response({"errors": ["validation errors"]},400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
