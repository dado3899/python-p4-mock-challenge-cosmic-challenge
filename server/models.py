from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
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
    # missions
    # Add serialization rules


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    field_of_study = db.Column(db.String, nullable = False)

    # Add relationship
    missions = db.relationship("Mission", back_populates="scientist")
    # Add serialization rules
    serialize_rules = ("-missions.scientist",)
    # Add validation
    # @validates('field_of_study')
    # def checkFOS(self, key, value):
    #     # print(type)
    #     if value and type(value) is str:
    #         return value
    #     else:
    #         raise ValueError("Not valid Field of study")

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable = False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable = False)
    # Add relationships
    planet = db.relationship("Planet", backref="missions")
    scientist = db.relationship("Scientist", back_populates = "missions")
    # Add serialization rules
    serialize_rules = ('-planet.missions','-scientist.missions')
    # Add validation
    @validates("scientist_id","planet_id")
    def validate_id(self,key,value):
        if key == "scientist_id":
            scientist = Scientist.query.filter(Scientist.id == value).first()
            if scientist:
                return value
        elif key == "planet_id":
            planet = Planet.query.filter(Planet.id == value).first()
            if planet:
                return value
        raise ValueError("Not valid ID")


# add any models you may need.
