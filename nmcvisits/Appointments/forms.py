from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError
from nmcvisits.Hospitals.helpers import getDepartments


class CreateAppointment(FlaskForm):
    appointmentDate = DateField("Appointment requested Date", validators=[DataRequired()])
    department = SelectMultipleField("Departments to visit", validators=[DataRequired()], choices=getDepartments)
    submit = SubmitField('Create Appointment')

    def validate_appointmentDate(self, appointmentDate):
        if appointmentDate.data <= datetime.today().date():
            raise ValidationError("Requested Date for visit cannot be in the past. please choose another date")
    # validate date here using a custom validator function
    # program the app so that admin can decide which days can be visiting days
