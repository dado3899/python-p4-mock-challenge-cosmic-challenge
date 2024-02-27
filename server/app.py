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

class scientistsRoute(Resource):
    def get(self):
        scientists = Scientist.query.all()
        scientistsDict = []

        for scientist in scientists:
            scientistsDict.append(scientist.to_dict(rules=('-missions',)))
        
        return scientistsDict,200
    def post(self):
        try:
            data = request.get_json()
            s = Scientist(
                name=data['name'],
                field_of_study=data['field_of_study'],
            )
            db.session.add(s)
            db.session.commit()
            return s.to_dict(),201
        except Exception as e:
            print(e)
            return {"errors": ["validation errors"]},400

class scientistsByIdRoute(Resource):
    def get(self,id):
        scientist_by_id = Scientist.query.filter(Scientist.id==id).first()
        if scientist_by_id:
            #Good  route
            return scientist_by_id.to_dict(),200
        else:
            return {"error": "Scientist not found"},400
    
    def patch(self,id):
        scientist_by_id = Scientist.query.filter(Scientist.id==id).first()
        if scientist_by_id:
            #Good  route
            try:
                data = request.get_json()
                for attr in data:
                    setattr(scientist_by_id,attr,data[attr])
                db.session.add(scientist_by_id)
                db.session.commit()
                return scientist_by_id.to_dict(),202
            except Exception as e:
                print(e)
                return {"errors": ["validation errors"]},400
        else:
            return {"error": "Scientist not found"},404
        
    def delete(self,id):
        scientist_by_id = Scientist.query.filter(Scientist.id==id).first()
        if scientist_by_id:
            #Good  route
            allMissions = Mission.query.filter(Mission.scientist_id==id).all()
            for mission in allMissions:
                db.session.delete(mission)
            db.session.delete(scientist_by_id)
            db.session.commit()
            return {}, 204
        else:
            return {"error": "Scientist not found"},404

class planetsRoute(Resource):
    def get(self):
        planets = Planet.query.all()
        planetsDict = []

        for planet in planets:
            planetsDict.append(planet.to_dict(rules=('-missions',)))
        
        return planetsDict,200

class missionsRoute(Resource):
    def post(self):
        try:
            data = request.get_json()
            m = Mission(
                name=data['name'],
                planet_id=data['planet_id'],
                scientist_id=data['scientist_id']
            )
            db.session.add(m)
            db.session.commit()
            return m.to_dict(),201

        except Exception as e:
            print(e)
            return {"errors": ["validation errors"]},400
api.add_resource(scientistsRoute,'/scientists')
api.add_resource(scientistsByIdRoute,'/scientists/<id>')
api.add_resource(planetsRoute,'/planets')
api.add_resource(missionsRoute,'/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
