from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from webbrowser import get
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from nmcvisits.models import User, Appointment, Departments, AllowedDaysToVisit # ,VisitedDepartments
from nmcvisits.helpers import getDepartments, notYetAllowedDays


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

class CreateAppointment(FlaskForm):
    appointmentDate = DateField("Appointment requested Date", validators=[DataRequired()])
    department = SelectMultipleField("Departments to visit", validators=[DataRequired()], choices=getDepartments)
    submit = SubmitField('Create Appointment')

    def validate_appointmentDate(self, appointmentDate):
        if appointmentDate.data <= datetime.today().date():
            raise ValidationError("Requested Date for visit cannot be in the past. please choose another date")

    # validate date here using a custom validator function
    # program the app so that admin can decide which days can be visiting days

class AddDepartments(FlaskForm):
    department = StringField("Department Name", validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Add Department')

    def validate_department(self, department):
        dpt =  Departments.query.filter_by(departmentName=department.data.strip().lower().title()).first()
        if dpt:
            raise ValidationError("Department is already available.")

class UpdateVisitingDays(FlaskForm):
    
    day = SelectField("Day", choices = notYetAllowedDays, validators=[DataRequired()])
    submit = SubmitField('Update Visiting Days')

    #def validate_day(self, day):
     #   if day == AllowedDaysToVisit.query.filter_by(day=str(day.data)).first():
      #      raise ValidationError("Day is already added to allowed days. select another day.")
        # update code so it is only showing days that are not allowed

