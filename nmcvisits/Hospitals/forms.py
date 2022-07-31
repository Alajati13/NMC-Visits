from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from nmcvisits.models import Departments
from nmcvisits.Hospitals.helpers import notYetAllowedDays, getAllowedDaysToVisit


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
