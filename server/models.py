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
    missions = relationship('Mission', back_populates='planet')

    # Add serialization rules
    serialize_rules = ('-missions.planet',)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    field_of_study = db.Column(db.String, nullable=False)

    # Add relationship
    missions = relationship('Mission', back_populates='scientist')

    # Add serialization rules
    serialize_rules = ('-missions.scientist',)

    # Add validation
    @validates('name','field_of_study')
    def validate_exist(self,key,value):
        if value:
            return value
        else:
            raise ValueError(f"Not valid {key}")


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    scientist = relationship('Scientist', back_populates = 'missions')
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    planet = relationship('Planet', back_populates='missions')

    # Add serialization rules
    serialize_rules = ('-planet.missions','-scientist.missions')

    # Add validation
    @validates('scientist_id','planet_id','name')
    def validate_exist(self,key,value):
        if( key == 'scientist_id'):
            if not Scientist.query.filter(Scientist.id==value).first(): 
                raise ValueError(f"Not valid {key}")
        elif( key == 'planet_id' ):
            if not Planet.query.filter(Planet.id==value).first(): 
                raise ValueError(f"Not valid {key}")
        if value:
            return value
        else:
            raise ValueError(f"Not valid {key}")

# add any models you may need.
