from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nmc.db'
db = SQLAlchemy(app)
db.create.all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    company = db.Column(db.String(100))
    jobTitle = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    imageFile = db.Column(db.String(20), nullable=False, default='default.jpg')
    appointment = db.relationship('Appointments', backref='visitor', lazy=True)

    #def __repr__(self):
     #   result = self.firstName +"\n" + self.lastName
      #  return result

        #return f"User('{self.firstName}' '{self.lastName}'\nJob Title : '{self.jobTitle}'\nCompany : '{self.company}'\nEmail : '{self.email}'\nPhone : '{self.phone}'\nImage File'{self.imageFile}')"

class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointmentDate = db.Column(db.DateTime, nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now)
    visitor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


if __name__ == '__main__':
    app.run(debug=True)