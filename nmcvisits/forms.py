from datetime import datetime
from email.policy import default
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectMultipleField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from nmcvisits.models import User, Appointment, Departments, EMIRATES, Weekdays, Hospital
from nmcvisits.helpers import getDepartments

class RegistrationForm(FlaskForm):
    username = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField("Password",validators=[DataRequired(), Length(min=8, max=20), Regexp("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$", message="Password should be 8 characters at least and contain an upper case letter, a lower case letter, and a number")])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        user =  User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already used. please register using a different email")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField("Password",validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    username = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    jobTitle = StringField("Job Title", validators=[DataRequired(), Length(min=2, max=100)])
    company = StringField("Company", validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=8, max=100)])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(["jpg","png","bmp","jpeg","svg"])])
    submit = SubmitField('Update')

def getHospitals():
    hospitals = []
    rows = Hospital.query.all()
    for row in rows:
        hospitals.append((row.id,row.name))
    return hospitals

class CreateAppointment(FlaskForm):
    appointmentDate = DateField("Appointment Requested Date", validators=[DataRequired()])
    hospital = SelectField("Hospital to Visit", validators=[DataRequired()], choices=getHospitals)
    department = SelectMultipleField("Departments", validators=[DataRequired()], choices=getDepartments)
    submit = SubmitField('Create Appointment')
    def validate_appointmentDate(self, appointmentDate):
        if appointmentDate.data <= datetime.today().date():
            raise ValidationError("Requested Date for visit cannot be in the past. please choose another date")
    # validate date here using a custom validator function
    # program the app so that admin can decide which days can be visiting days

class AddDepartments(FlaskForm):
    name = StringField("Department Name", validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Add Department')

    def validate_name(self, name):
        department =  Departments.query.filter_by(name=name.data.strip().lower().title()).first()
        if department:
            raise ValidationError("Department is already available.")

class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    submit = SubmitField("Request Password Reset")
    
    def validate_email(self, email):
        user =  User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email. You must register first.")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password",validators=[DataRequired(), Length(min=8, max=20), Regexp("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$", message="Password should be 8 characters at least and contain an upper case letter, a lower case letter, and a number")])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")

def getAllDepartments():
    departments = []
    rows = Departments.query.all()
    for row in rows:
        departments.append(row.name)
    return departments

class AddHospital(FlaskForm):
    name = StringField("Hospital Name", validators=[DataRequired(), Length(min=2, max=100)])
    city = SelectField("City", validators=[DataRequired()], choices=EMIRATES)
    address = StringField("Address", validators=[DataRequired(), Length(min=2, max=200)])
    departments = SelectMultipleField("Departments", validators=[DataRequired()], choices=getAllDepartments)
    visitingDays = SelectMultipleField("Visiting Days", validators=[DataRequired()], choices=Weekdays.getWeekdays)
    submit = SubmitField('Add Hospital')

class EditHospital(FlaskForm):
    hospital_id = HiddenField("Hospital ID", validators=[DataRequired()])
    name = StringField("Hospital Name", validators=[DataRequired(), Length(min=2, max=100)])
    city = SelectField("City", validators=[DataRequired()], choices=EMIRATES)
    address = StringField("Address", validators=[DataRequired(), Length(min=2, max=200)])
    departments = SelectMultipleField("Departments", validators=[DataRequired()], choices=getAllDepartments)
    visitingDays = SelectMultipleField("Visiting Days", validators=[DataRequired()], choices=Weekdays.getWeekdays)
    submit = SubmitField('Update Hospital Details')


def getRemainingDepartments():
    pass

# might not use it, but use another way to add department directly from a grid ov available departments
class AddHospitalDepartments(FlaskForm):
    departments = SelectMultipleField("Departments", validators=[DataRequired()], choices=getRemainingDepartments)
    submit = SubmitField('Add Department')

class SetHospitalVisitingDays(FlaskForm):
    days = SelectMultipleField("Days", validators=[DataRequired()], choices=Weekdays.getWeekdays)
    submit = SubmitField('Set Days')
