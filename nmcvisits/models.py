from datetime import datetime, timedelta
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
    visitor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    departments = db.relationship('VisitedDepartments', backref='visitedDepartments', lazy=True)
    
    def __repr__(self):
        return f"Appointment('{self.visitor_id}', '{self.appointmentDate}')"

    
class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departmentName = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Departments('{self.departmentName}')"

class VisitedDepartments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    def __repr__(self):
        return f"Visited Departments('{self.department_id}' for appointment '{self.appointment_id}')"

class AllowedDaysToVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String, nullable=False, unique=True)

