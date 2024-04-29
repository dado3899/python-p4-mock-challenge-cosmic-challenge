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

@app.route('/planets', methods=["GET"])
def all_planets():
    all_pl = Planet.query.all()
    r_l = []
    for pl in all_pl:
        r_l.append(pl.to_dict(rules = ("-missions",)))
    return r_l

@app.route('/missions', methods=["POST"])
def all_missions():
    try:
        data = request.get_json()
        m = Mission(
            name = data['name'],
            scientist_id = data['scientist_id'],
            planet_id = data['planet_id']
        )
        db.session.add(m)
        db.session.commit()
        return m.to_dict(),201
    except:
        return {"errors": ["validation errors"]},400

@app.route('/scientists', methods = ["GET","POST"])
def all_scientist():
    if request.method == "GET":
        all_sc = Scientist.query.all()
        return [sc.to_dict(rules=("-missions",)) for sc in all_sc]
    elif request.method == "POST":
        try:
            data = request.get_json()
            sc = Scientist(
                name = data["name"],
                field_of_study = data['field_of_study']
            )
            db.session.add(sc)
            db.session.commit()
            return sc.to_dict(rules=("-missions",)),200
        except Exception as e:
            return {"errors": ["validation errors"]},400
    

@app.route('/scientists/<int:id>', methods=["GET","PATCH","DELETE"])
def one_scientist(id):
    one_sc = Scientist.query.filter(Scientist.id == id).first()
    if one_sc:
        if request.method == "GET":
            return one_sc.to_dict(),200
        elif request.method == "PATCH":
            try:
                data = request.get_json()
                for attr in data:
                    setattr(one_sc,attr,data[attr])
                db.session.add(one_sc)
                db.session.commit()
                return one_sc.to_dict(rules=('-missions',)),202
            except:
                return {"errors": ["validation errors"]},400
        elif request.method == "DELETE":
            # Mission.query.filter(Mission.scientist_id==id).all()
            db.session.delete(one_sc)
            db.session.commit()
            return {},204
    else:
        return {"error": "Scientist not found"},404

if __name__ == '__main__':
    app.run(port=5555, debug=True)
