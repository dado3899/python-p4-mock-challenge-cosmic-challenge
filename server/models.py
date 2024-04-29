from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = relationship("Mission", cascade='delete,all', back_populates="planet")
    # Add serialization rules
    serialize_rules = ('-missions.planet',)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    field_of_study = db.Column(db.String,nullable = False)

    # Add relationship
    missions = relationship("Mission",  cascade='delete,all',back_populates="scientist")
    # Add serialization rules
    serialize_rules = ('-missions.scientist',)
    # Add validation
    @validates('field_of_study','name')
    def validate_exist(self,key,value):
        if value:
            return value
        else:
            raise ValueError(f"Not valid {key}")

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable = False)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'),nullable = False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'),nullable = False)

    planet = relationship("Planet", back_populates="missions")
    scientist = relationship("Scientist", back_populates="missions")



    # Add serialization rules
    serialize_rules = ("-planet.missions", "-scientist.missions")
    # Add validation
    @validates('name','scientist_id','planet_id')
    def validate_exist(self,key,value):
        if value:
            return value
        else:
            raise ValueError(f"Not valid {key}")

# add any models you may need.
