from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Legnth, Email, EqualTo

class RegistrationForm(FlaskForm):
    firstName = StringField("First Name", validators=[DataRequired(), Legnth(min=1, max=20)])
    lastName = StringField("Last Name", validators=[DataRequired(), Legnth(min=1, max=20)])
    email = StringField("Email", validators=[DataRequired(), email(), Legnth(max=100)])
    password = PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
