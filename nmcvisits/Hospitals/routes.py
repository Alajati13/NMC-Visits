from flask import Blueprint, render_template, url_for, redirect, request
from nmcvisits import db
from nmcvisits.Hospitals.forms import AddDepartments, UpdateVisitingDays
from nmcvisits.models import Departments, Appointment, AllowedDaysToVisit, VisitedDepartments
from flask_login import login_required
from nmcvisits.Hospitals.helpers import getDepartments, getAllowedDaysToVisit


hospitals = Blueprint("hospitals", __name__)



@hospitals.route("/departments", methods=["GET", "POST"])
@login_required
def departments():
    departments = getDepartments()
    form = AddDepartments()
    if form.validate_on_submit():
        department = Departments(departmentName = form.department.data.strip().title())
        db.session.add(department)
        db.session.commit()
        return redirect(url_for("hospitals.departments"))
    return render_template("departments.html", departments=departments, sidebar = 4, form=form)


@hospitals.route("/deleteDepartment", methods=["POST"])
@login_required
def deleteDepartment():
    departmentName = request.form.get("departmentName")
    department = Departments.query.filter_by(departmentName=departmentName).first()
    db.session.delete(department)
    rows = VisitedDepartments.query.filter_by(department_id=department.id).all()
    for row in rows:
        apt_id = row.appointment_id
        if len(VisitedDepartments.query.filter_by(appointment_id=apt_id).all()) == 1:
            appointment = Appointment.query.filter_by(id=apt_id).first()
            db.session.delete(appointment)
        db.session.delete(row)

    db.session.commit()
    return redirect(url_for("hospitals.departments"))


@hospitals.route("/allowedDaysToVisit", methods=["POST", "GET"])
@login_required
def allowedDaysToVisit():
    form = None
    form = UpdateVisitingDays()
    if form.validate_on_submit():
        day = AllowedDaysToVisit(day=form.day.data) 
        db.session.add(day)
        db.session.commit()       
        return redirect(url_for("hospitals.allowedDaysToVisit"))
    return render_template("allowedDaysToVisit.html", days = getAllowedDaysToVisit(), sidebar = 4, form=UpdateVisitingDays())

@hospitals.route("/deleteDay", methods=["POST"])
@login_required
def deleteDay():
    dayName = request.form.get("day")
    day = AllowedDaysToVisit.query.filter_by(day=dayName).first()
    db.session.delete(day)
    db.session.commit()
    return redirect(url_for("hospitals.allowedDaysToVisit"))