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

api = Api(app)

@app.route('/')
def home():
    return ''

class All_Scientist(Resource):
    def get(self):
        sc = Scientist.query.all()
        return [scientist.to_dict(rules=('-missions',)) for scientist in sc]
    def post(self):
        try:
            data = request.get_json()
            scientist = Scientist(name = data["name"], field_of_study = data['field_of_study'])
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(rules=('-missions',)),201
        except Exception as e:
            print(e)
            return {"errors": ["validation errors"]},400

class One_Scientist(Resource):
    def get(self,id):
        scientist = Scientist.query.filter(Scientist.id==id).first()
        if scientist:
            return scientist.to_dict()
        else:
            return {
                "error": "Scientist not found"
            },404
    def patch(self,id):
        scientist = Scientist.query.filter(Scientist.id==id).first()
        if scientist:
            try:
                data = request.get_json()
                for key in data:
                    setattr(scientist,key,data[key])
                db.session.add(scientist)
                db.session.commit()
                return scientist.to_dict(rules=('-missions',)),202
            except Exception as e:
                print(e)
                return { "errors": ["validation errors"]},400
        else:
            return {
                "error": "Scientist not found"
            },404
    def delete(self,id):
        scientist = Scientist.query.filter(Scientist.id==id).first()
        if scientist:
            scientist_missions = Mission.query.filter(Mission.scientist_id == id).all()
            for mission in scientist_missions:
                db.session.delete(mission)
            db.session.delete(scientist)
            db.session.commit()

            return {},204
        else:
            return {
                "error": "Scientist not found"
            },404

class All_planets(Resource):
    def get(self):
        ap = Planet.query.all()
        r_l = []
        for planet in ap:
            r_l.append(planet.to_dict(rules=('-missions',)))
        return r_l
    
class All_Missions(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_mission = Mission(name = data['name'],planet_id = data['planet_id'], scientist_id = data['scientist_id'])
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(),201
        except:
            return { "errors": ["validation errors"] },400
api.add_resource(All_Scientist,'/scientists')
api.add_resource(One_Scientist,'/scientists/<int:id>')
api.add_resource(All_planets,'/planets')
api.add_resource(All_Missions,'/missions')




if __name__ == '__main__':
    app.run(port=5555, debug=True)
