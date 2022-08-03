from calendar import week
from datetime import datetime, timedelta
from enum import unique
from time import timezone
from nmcvisits import db, login_manager, app
from flask_login import UserMixin
import jwt

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    company = db.Column(db.String())
    jobTitle = db.Column(db.String())
    phone = db.Column(db.String())
    imageFile = db.Column(db.String(20), nullable=False, default='default.jpg')
    role = db.Column(db.String(20), nullable=False, default="Visitor")
    notes = db.Column(db.String(300))
    appointments = db.relationship('Appointment', backref='visitor', lazy=True)

    def get_reset_token(self, expiration=1800):
        resetToken = jwt.encode({"user_id" : self.id, "exp" : datetime.now() + timedelta(seconds=expiration)}, app.config["SECRET_KEY"], algorithm = "HS256")
        return resetToken
    
    @staticmethod
    def verify_reset_token(token):
        #s = Serializer(app.config["SECRET_KEY"])
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"],leeway=timedelta(seconds=10), algorithms=["HS256"])
        except:
            return None
        user_id = data.get("user_id")
        return User.query.get(user_id)

    def __repr__(self):
        return f"User : {self.username} - Email : {self.email}\n"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointmentDate = db.Column(db.DateTime, nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='Pending Approval')
    visitor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    departments = db.relationship('VisitedDepartments', backref='visitedDepartments', lazy=True)
    hospital = db.relationship('Hospital', backref='hospital', lazy=True)

    def __repr__(self):
        return f"Appointment('{self.visitor_id}', '{self.appointmentDate}')"

EMIRATES = ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm AlQuwain"]
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    departments = db.relationship('HospitalDepartments', backref='hospitalDepartments', lazy=True)
    visitingDays = db.relationship('HospitalDaysToVisit', backref='visitingHospitalDays', lazy=True)

class HospitalDepartments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    department = db.Column(db.String(50), db.ForeignKey('departments.name'), nullable=False)
    departmentObject = db.relationship('Departments', backref='hopsital', lazy=True)

class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"Departments('{self.departmentName}')"

class VisitedDepartments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    departmentNames = db.relationship('Departments', backref='departments', lazy=True)
    
    def __repr__(self):
        return f"Visited Departments('{self.department_id}' for appointment '{self.appointment_id}')"

class Weekdays():
    @staticmethod
    def getWeekdays():
        WEEKDAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        weekdays = []
        for day in WEEKDAYS:
            weekdays.append(day)
        return weekdays

class HospitalDaysToVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String, nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)

