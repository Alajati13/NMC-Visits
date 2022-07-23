from datetime import datetime
from nmcvisits import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    jobTitle = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    imageFile = db.Column(db.String(20), nullable=False, default='default.jpg')
    appointments = db.relationship('Appointment', backref='visitor', lazy=True)


    def __repr__(self):
        if self.firstName == None and self.lastName == None:
            return f"User : Name Still pending - Email : {self.email}\n"
        return f"User : {self.firstName} {self.lastName} - Email : {self.email}\n"

class Appointment(db.Model):
    departments = ["Cardiology", "Internal Medicine", "Pediatrics", "ENT", "Nephrology"]
    id = db.Column(db.Integer, primary_key=True)
    appointmentDate = db.Column(db.DateTime, nullable=False)
    visitedDepartments = db.Column(db.String(150), nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now)
    visitor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Appointment('{self.visitor_id}', '{self.appointmentDate}', '{self.visitedDepartments}')"
