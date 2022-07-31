from nmcvisits.models import Departments, AllowedDaysToVisit



def getAllowedDaysToVisit():
    allowedDaysToVisit = []
    rows = AllowedDaysToVisit.query.all()
    for row in rows:
        allowedDaysToVisit.append(row.day)
    return allowedDaysToVisit

def notYetAllowedDays():
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    notYetAllowedDays = weekdays
    rows = AllowedDaysToVisit.query.all()
    for row in rows:
        notYetAllowedDays.remove(row.day)
    return notYetAllowedDays

def getDepartments():
    departments = []
    for row in Departments.query.all():
        departments.append(row.departmentName)
        departments.sort()
    return departments
