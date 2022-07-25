from csv import field_size_limit
from dataclasses import Field
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from nmcvisits.models import User, Appointment, Departments # ,VisitedDepartments

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
    '''
     departments = []
    for entry in Departments.query.all():
        departments.append(entry["departmentName"])

    '''
   
    appointmentDate = DateField("Appointment requested Date", validators=[DataRequired()])
    #department = SelectMultipleField("Departments to visit", choices=[departments])
    submit = SubmitField('Create Appointment')

class AddDepartments(FlaskForm):
    department = StringField("Department Name", validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Add Department')
    def validate_department(self, department):
        dpt =  Departments.query.filter_by(departmentName=department.data).first()
        if dpt:
            raise ValidationError("Department is already available.")

'''
class DeleteDepartments(FlaskForm):
    department = StringField("Department Name", validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Add Department')
'''
