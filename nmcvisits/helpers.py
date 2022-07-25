from nmcvisits.models import User, Appointment, Departments # ,VisitedDepartments
from nmcvisits import db


def getDepartments():
    departments = []
    for row in Departments.query.all():
        departments.append(row.departmentName)
        departments.sort()
    return departments


