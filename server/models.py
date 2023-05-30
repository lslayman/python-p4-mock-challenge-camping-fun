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

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    # Serialize rules needed for GET request for Activities in app.py
    serialize_rules = ('-campers.activities', '-signups.activity')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # An Activity has many Signups and has many Campers *through* Signups
    signups = db.relationship('Signup', backref='activity')
    campers = association_proxy('signups', 'camper', creator=lambda cmp: Signup(camper=cmp))

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    # Needed for GET request on app.py
    serialize_rules = ('-activities.campers', '-signups.camper')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # A Camper has many Signups, and have many Activity(s) *through* Signups
    signups = db.relationship("Signup", backref='camper')
    activities = association_proxy('signups', 'activity', creator=lambda act: Signup(activity=act))

    # Add validations to the Camper model:
    # must have a name
    # must have an age between 8 and 18
    @validates('name')
    def validates_name(self, key, name):
        if name:
            return name
        raise ValueError("Camper must have a name.")

    @validates('age')
    def validates_age(self, key, age):
        if 8 <= age <= 18:
            return age
        raise ValueError("Camper must be between 8 and 18 years-old.")

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'
    
class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    # Needed for POST request in app.py
    serialize_rules = ('-activity.signups', '-camper.signups')

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    # A Signup belongs to a Camper and belongs to an Activity
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    # Add validations to the Signup model:
    # must have a time between 0 and 23 (referring to the hour of day for the activity)
    @validates('time')
    def validate_time(self, key, time):
        if 0 <= time <= 23:
            return time
        raise ValueError("Time must be an integer between 0 and 23")


    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need. 