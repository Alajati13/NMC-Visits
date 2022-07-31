from flask import Blueprint, render_template, url_for, redirect, flash, request, send_from_directory, current_app
import os
from nmcvisits import db
from nmcvisits.Appointments.forms import CreateAppointment
from nmcvisits.models import Departments, User, Appointment, VisitedDepartments
from flask_login import login_required, current_user
from nmcvisits.Appointments.helpers import generatePDF
from nmcvisits.Appointments.helpers import sendConfirmationEmail


appointmentsBP = Blueprint("appointments", __name__)


@appointmentsBP.route("/createAppointment", methods=["POST", "GET"])
@login_required
def createAppointment():
    form = CreateAppointment()
    if form.validate_on_submit():
        appointment = Appointment(appointmentDate = form.appointmentDate.data, visitor_id = current_user.id)
        departments = form.department.data
        db.session.add(appointment)
        
        for dpt in departments:
            department = Departments.query.filter_by(departmentName = dpt).first()
            visitedDepartment = VisitedDepartments(appointment_id = appointment.id, department_id = department.id)
            db.session.add(visitedDepartment)
    
        db.session.commit()
        user = User.query.get(appointment.visitor_id)
        flash(f'Your appointment has been created. A confirmation email will be sent to you shortly.', 'success')
        sendConfirmationEmail(user, appointment)
        return redirect(url_for("appointments.createAppointment"))
    appointments = []
    rows = Appointment.query.filter_by(visitor_id=current_user.id)
    for row in rows:
        entry={}
        entry["appointmentDate"] = row.appointmentDate.date()
        entry['appointment_id'] = row.id
        dpts = VisitedDepartments.query.filter_by(appointment_id=row.id)
        listOfDpts = []
        for dpt in dpts:
            name = Departments.query.filter_by(id=dpt.department_id).first()
            listOfDpts.append(name.departmentName)
        entry["departments"] = listOfDpts
        appointments.append(entry)
    return render_template("createAppointment.html", sidebar = 6, form=form, appointments=appointments)

@appointmentsBP.route("/deleteAppointment", methods=["POST", "GET"])
@login_required
def deleteAppointment():
    appointment_id = request.form.get("appointment_id")
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    rows = VisitedDepartments.query.filter_by(appointment_id=appointment_id).all()
    for row in rows:
        db.session.delete(row)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for("appointments.createAppointment"))



@appointmentsBP.route("/printAppointment", methods=["POST", "GET"])
@login_required
def printAppointment():
    if request.method == "POST":
        appointment_id = request.form.get("appointment_id")
        
        generatePDF(appointment_id)
        path = os.path.join(current_app.root_path, "static/Visits_Printouts")
        filename = (appointment_id + ".pdf")
        try:
            return send_from_directory(path, filename, as_attachment=True)
        except:
            flash(f'Unable to download the PDF confirmation. Please inform the Security staff when arriving', 'danger')
            return redirect(url_for("appointments.createAppointment"))
    return "<h1> This page is not available </h1>"
    #return render_template("printout.html", sidebar = False)

@appointmentsBP.route('/appointment/<int:number>')
@login_required
def allow(number):
    appointment = Appointment.query.filter_by(id=number).first()
    user = User.query.filter_by(id=appointment.visitor_id).first()
    departments_id = VisitedDepartments.query.filter_by(appointment_id=appointment.id).all()
    departments = []
    for dpt in departments_id:
        department = Departments.query.filter_by(id=dpt.department_id).first()
        departments.append(department.departmentName)
    imageFile = url_for("static", filename="profile_photos/" + user.imageFile)
    return render_template("appointment.html", sidebar = 6, appointment=appointment, user=user, departments=departments, path=imageFile)


@appointmentsBP.route("/appointments", methods=["POST", "GET"])
@login_required
def appointments():
    allAppointments = []
    appointments = Appointment.query.all()
    for appointment in appointments:
        user = User.query.filter_by(id=appointment.visitor_id).first()
        departments_id = VisitedDepartments.query.filter_by(appointment_id=appointment.id).all()
        departments = []
        for dpt in departments_id:
            department = Departments.query.filter_by(id=dpt.department_id).first()
            departments.append(department.departmentName)
        
        createdAppointment = {}
        createdAppointment["appointment"] = appointment
        createdAppointment["user"] = user
        createdAppointment["departments"] = departments
        allAppointments.append(createdAppointment)
    return render_template("appointments.html", sidebar = False, title = "Appointments", data=allAppointments)

