from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from nmcvisits.models import User

class RegistrationForm(FlaskForm):
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
