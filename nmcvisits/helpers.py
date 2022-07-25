from nmcvisits.models import User, Appointment, Departments, AllowedDaysToVisit # ,VisitedDepartments
from nmcvisits import db


def getDepartments():
    departments = []
    for row in Departments.query.all():
        departments.append(row.departmentName)
        departments.sort()
    return departments


def getAllowedDaysToVisit():
    allowedDaysToVisit = []
    rows = AllowedDaysToVisit.query.all()
    for row in rows:
        allowedDaysToVisit.append(row.day)
    return allowedDaysToVisit
