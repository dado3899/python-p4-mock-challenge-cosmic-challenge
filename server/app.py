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

@app.route('/scientist', methods = ["GET","POST"])
def scientistAll():
    if request.method == "GET":
        all_scientist = Scientist.query.all()
        all_scientist_dict = []
        for scientist in all_scientist:
            scientist.serialize_rules = ('-missions',)
            all_scientist_dict.append(scientist.to_dict())
        return make_response(all_scientist_dict,200)
    elif request.method == "POST":
        try:
            data = request.get_json()
            new_scientist = Scientist(name = data["name"], field_of_study = data["field_of_study"])
            db.session.add(new_scientist)
            db.session.commit()
            new_scientist.serialize_rules = ('-missions',)
            return make_response(new_scientist.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]})
        
@app.route('/scientist/<id>', methods = ["GET","PATCH","DELETE"])
def scientistSingle(id):
    single_scientist = Scientist.query.filter(Scientist.id == id).first()
    if single_scientist:
        if request.method == "GET":
            return make_response(single_scientist.to_dict(),200)     
        elif request.method == "PATCH":
            try:
                data = request.get_json()
                for attr in data:
                    setattr(single_scientist,attr,data[attr])
                db.session.add(single_scientist)
                db.session.commit()
                single_scientist.serialize_rules = ('-missions',)
                return make_response(single_scientist.to_dict(), 200)
            except:
                return make_response({"errors": ["validation errors"]},400)
        elif request.method == "DELETE":
            for mission in single_scientist.missions:
                db.session.delete(mission)
            db.session.delete(single_scientist)
            db.session.commit()
            return make_response({},204)
    else:
        return make_response({"error": "Scientist not found"},400)

@app.route("/planets")
def planetsAll():
    if request.method == "GET":
        all_planet = Planet.query.all()
        all_planet_dict = []
        for planet in all_planet:
            # planet.serialize_rules = ('-missions',)
            all_planet_dict.append(planet.to_dict())
        return make_response(all_planet_dict,200)
    
@app.route("/missions", methods = ["POST"])
def missionPost():
    if request.method == "POST":
        try:
            data = request.get_json()
            new_mission = Mission(name = data["name"], planet_id = data["planet_id"], scientist_id = data["scientist_id"])
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(),201)
        except:
           return make_response({"errors": ["validation errors"]},400)
if __name__ == '__main__':
    app.run(port=5555, debug=True)
