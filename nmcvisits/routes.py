from datetime import datetime
import secrets
import os
from flask import render_template, url_for, redirect, flash, request, send_from_directory
from nmcvisits import app, db, bcrypt, mail
from nmcvisits.forms import AddHospital, RegistrationForm, LoginForm, UpdateProfileForm ,AddDepartments, CreateAppointment, RequestResetForm, ResetPasswordForm, EditHospital
from nmcvisits.models import Weekdays, Departments, Hospital, User, Appointment, VisitedDepartments, HospitalDepartments, HospitalDaysToVisit
from flask_login import login_user, current_user, logout_user, login_required
from nmcvisits.helpers import sendResetEmail, savePicture, generatePDF, isAdmin, sendConfirmationEmail, isProfileComplete
import random
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title = "Home",)

@app.route("/about")
def about():
    return render_template("about.html", title = "About",)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            nextPage = request.args.get("next") 
            return redirect(nextPage) if nextPage else redirect(url_for("home"))
        else:
            flash("Login Unsuccesful. Please check email and password", "danger")
    return render_template("login.html", title = "Login", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pasword = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username = form.username.data.strip().title(), email = form.email.data, password = hashed_pasword)
        db.session.add(user)
        db.session.commit()
    
        flash(f'Your account has been created. Please Log in and complete your profile data to proceed.', 'success')
        return redirect("/login")
    return render_template("register.html", title = "Register", form=form)    

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

# do profile so that it shows one view (no sidebar) and there is a big edit profile button that add sidebar with editing tools 
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateProfileForm() 
    if form.validate_on_submit():
        if form.picture.data:
            pictureFile = savePicture(form.picture.data)
            if current_user.imageFile != "default.jpg":
                oldPicturePath = os.path.join(app.root_path, "static/Profile_Photos", current_user.imageFile)
                os.remove(oldPicturePath)
            current_user.imageFile = pictureFile
        current_user.username = form.username.data.strip().title()
        current_user.jobTitle = form.jobTitle.data.strip().title()
        current_user.company = form.company.data.strip().title()
        current_user.phone = form.phone.data.strip()
        db.session.commit()
        flash("your profile has been updated", "success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.jobTitle.data = current_user.jobTitle
        form.company.data = current_user.company
        form.phone.data = current_user.phone
    imageFile = url_for("static", filename="profile_photos/" + current_user.imageFile)
    return render_template("profile.html", title = "Profile", sidebar = 7, imageFile=imageFile, form=form)


@app.route("/departments", methods=["GET", "POST"])
@login_required
@isAdmin
def departments():
    departments = Departments.query.all()
    form = AddDepartments()
    if form.validate_on_submit():
        department = Departments(name = form.name.data.strip().lower().title())
        db.session.add(department)
        db.session.commit()
        return redirect(url_for("departments"))
    return render_template("departments.html", departments=departments, sidebar = 4, form=form)

'''
@app.route("/deleteDepartment", methods=["POST"])
@login_required
@isAdmin
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
    return redirect(url_for("departments"))
'''



@app.route("/createAppointment", methods=["POST", "GET"])
@login_required
@isProfileComplete
def createAppointment():
    form = CreateAppointment()
    if form.validate_on_submit():
        appointment = Appointment(appointmentDate = form.appointmentDate.data, visitor_id = current_user.id, hospital_id=form.hospital.data)
        departments = form.department.data
        db.session.add(appointment)
        for dpt in departments:
            department = Departments.query.filter_by(name = dpt).first()
            visitedDepartment = VisitedDepartments(appointment_id = appointment.id, department_id = department.id)
            db.session.add(visitedDepartment)
        db.session.commit()
        flash(f'Your appointment has been created. A confirmation email will be sent to you shortly.', 'success')
        # sendConfirmationEmail(user, appointment)
        return redirect(url_for("createAppointment"))
    appointments = []
    appointments = Appointment.query.filter_by(visitor_id=current_user.id)
    return render_template("createAppointment.html", sidebar = 6, form=form, appointments=appointments)

@app.route("/deleteAppointment", methods=["POST", "GET"])
@login_required
@isProfileComplete
def deleteAppointment():
    if request.method == "POST":
        appointment_id = request.form.get("appointment_id")
        print("===========================================")
        print(appointment_id)
        appointment = Appointment.query.filter_by(id=appointment_id).first()
        for vDepartment in appointment.departments:
            db.session.delete(vDepartment)
        db.session.delete(appointment)
        db.session.commit()
    return redirect(url_for("createAppointment"))


@app.route("/users", methods=["POST", "GET"])
@login_required
@isAdmin
def users():
    users = User.query.all()
    return render_template("users.html", sidebar = False, users=users)

@app.route("/printAppointment", methods=["POST", "GET"])
@login_required
@isProfileComplete
def printAppointment():
    if request.method == "POST":
        appointment_id = request.form.get("appointment_id")
        
        generatePDF(appointment_id)
        path = os.path.join(app.root_path, "static/Visits_Printouts")
        filename = (appointment_id + ".pdf")
        try:
            return send_from_directory(path, filename, as_attachment=True)
        except:
            flash(f'Unable to download the PDF confirmation. Please inform the Security staff when arriving', 'danger')
            return redirect(url_for("createAppointment"))
    return "<h1> This page is not available </h1>"
    #return render_template("printout.html", sidebar = False)

@app.route('/appointment/<int:number>')
@login_required
@isAdmin
def allow(number):
    appointment = Appointment.query.filter_by(id=number).first()
    user = User.query.filter_by(id=appointment.visitor_id).first()
    departments = VisitedDepartments.query.filter_by(appointment_id=appointment.id).all()
    imageFile = url_for("static", filename="profile_photos/" + user.imageFile)
    return render_template("appointment.html", sidebar = 6, appointment=appointment, user=user, path=imageFile)

@app.route("/generateRandomAppointments", methods=["POST", "GET"])
@login_required
@isAdmin
def generateRandomAppointments():
    if request.method == "POST":
        for i in range(10):
            users = User.query.all()
            user = random.choice(users)
            hospitals = Hospital.query.all()
            hospital = random.choice(hospitals)
            departments = hospital.departments
            dpt = random.choice(departments)
            appointment = Appointment(appointmentDate = datetime.now(), visitor_id = user.id, hospital_id=hospital.id)
            db.session.add(appointment)
            db.session.commit()
            hDepartment = dpt.departmentObject
            dpt_id = hDepartment.id
            visitedDepartment = VisitedDepartments(appointment_id=appointment.id, department_id=dpt_id)
            db.session.add(visitedDepartment)
            db.session.commit()
    return redirect("/appointments")




@app.route("/appointments", methods=["POST", "GET"])
@login_required
@isAdmin
def appointments():
    appointments = Appointment.query.all()

    if request.method == "GET":
        showPendingApproval = True
        showApproved = True
        showRejected = True
        hideDepartments = False
        hideNotes = False
    else:
        if request.form.get("showPendingApproval"):
            showPendingApproval = True
        else:
            showPendingApproval = False
        if request.form.get("showApproved"):
            showApproved = True
        else:
            showApproved = False
        if request.form.get("showRejected"):
            showRejected = True
        else:
            showRejected = False
        if request.form.get("hideDepartments"):
            hideDepartments = True
        else:
            hideDepartments = False
        if request.form.get("hideNotes"):
            hideNotes = True
        else:
            hideNotes = False
        appointments = []
        if showPendingApproval:
            apts = Appointment.query.filter_by(status="Pending Approval")
            for apt in apts:
                appointments.append(apt)
        if showApproved:
            apts = Appointment.query.filter_by(status="Approved")
            for apt in apts:
                appointments.append(apt)
        if showRejected:
            apts = Appointment.query.filter_by(status="Rejected")
            for apt in apts:
                appointments.append(apt)
    return render_template("appointments.html", sidebar = 9, title = "Appointments", appointments=appointments, showPendingApproval=showPendingApproval, showApproved=showApproved, showRejected=showRejected, hideDepartments=hideDepartments, hideNotes=hideNotes)

@app.route("/approveAppointments", methods=["POST"])
@login_required
@isAdmin
def approveAppointments():
    if request.form.get("appointment_id"):
        id = request.form.get("appointment_id")
        appointment = Appointment.query.filter_by(id=id).first()
        appointment.status = "Approved"
        db.session.commit()
    # to be deleted. no use: appointments = Appointment.query.all()
    showPendingApproval = request.form.get("showPendingApproval")
    showApproved = request.form.get("showApproved")
    showRejected = request.form.get("showRejected")
    print("-------------------------------------------- show pending : ")
    print(showPendingApproval)
    hideDepartments = request.form.get("hideDepartments")
    if hideDepartments  == "True":
        hideDepartments = True
    else:
        hideDepartments = False
    hideNotes = request.form.get("hideNotes")
    if hideNotes  == "True":
        hideNotes = True
    else:
        hideNotes = False
    appointments = []
    if showPendingApproval == "True":
        apts = Appointment.query.filter_by(status="Pending Approval")
        for apt in apts:
            appointments.append(apt)
        showPendingApproval = True
    else:
        showPendingApproval = False
    if showApproved  == "True":
        apts = Appointment.query.filter_by(status="Approved")
        for apt in apts:
            appointments.append(apt)
        showApproved = True
    else:
        showApproved = False
    if showRejected  == "True":
        apts = Appointment.query.filter_by(status="Rejected")
        for apt in apts:
            appointments.append(apt)
        showRejected = True
    else:
        showRejected = False
    return render_template("appointments.html", sidebar = 9, title = "Appointments", appointments=appointments, showPendingApproval=showPendingApproval, showApproved=showApproved, showRejected=showRejected, hideDepartments=hideDepartments, hideNotes=hideNotes)


@app.route("/rejectAppointment", methods=["POST"])
@login_required
@isAdmin
def rejectAppointment():
    if request.form.get("appointment_id"):
        id = request.form.get("appointment_id")
        appointment = Appointment.query.filter_by(id=id).first()
        appointment.status = "Rejected"
        db.session.commit()
    # to be deleted. no use: appointments = Appointment.query.all()
    showPendingApproval = request.form.get("showPendingApproval")
    showApproved = request.form.get("showApproved")
    showRejected = request.form.get("showRejected")
    print("-------------------------------------------- show pending : ")
    print(showPendingApproval)
    hideDepartments = request.form.get("hideDepartments")
    if hideDepartments  == "True":
        hideDepartments = True
    else:
        hideDepartments = False
    hideNotes = request.form.get("hideNotes")
    if hideNotes  == "True":
        hideNotes = True
    else:
        hideNotes = False
    appointments = []
    if showPendingApproval == "True":
        apts = Appointment.query.filter_by(status="Pending Approval")
        for apt in apts:
            appointments.append(apt)
        showPendingApproval = True
    else:
        showPendingApproval = False
    if showApproved  == "True":
        apts = Appointment.query.filter_by(status="Approved")
        for apt in apts:
            appointments.append(apt)
        showApproved = True
    else:
        showApproved = False
    if showRejected  == "True":
        apts = Appointment.query.filter_by(status="Rejected")
        for apt in apts:
            appointments.append(apt)
        showRejected = True
    else:
        showRejected = False
    return render_template("appointments.html", sidebar = 9, title = "Appointments", appointments=appointments, showPendingApproval=showPendingApproval, showApproved=showApproved, showRejected=showRejected, hideDepartments=hideDepartments, hideNotes=hideNotes)

@app.route("/resetPassword", methods=["POST", "GET"])
def resetRequest():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendResetEmail(user)
        flash("An email has been sent with instruction to reset your password", "info")
        return redirect(url_for("login"))
    return render_template("resetrequest.html", title = "Reset Password", form=form)

@app.route("/resetPassword/<token>", methods=["POST", "GET"])
def resetToken(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("resetrequest"))    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pasword = bcrypt.generate_password_hash(form.password.data).decode("utf-8")    
        user.password = hashed_pasword
        db.session.commit()
        flash(f'Your password has been updated. Yu are now able to Login', 'success')
        return redirect("/login")
    return render_template("resetToken.html", title = "Reset Password", form=form)


@app.route("/hospitals", methods=["POST", "GET"])
@login_required
@isAdmin
def hospitals():
    hospitals = Hospital.query.all()
    hideDepartments = False
    hideDays = False
    if request.method == "POST":
        if request.form.get("hideDepartments"):
            hideDepartments = True
        if request.form.get("hideDays"):
            hideDays = True
    return render_template("hospitals.html", hospitals=hospitals, hideDepartments=hideDepartments, hideDays=hideDays)

@app.route("/addHospital", methods=["POST", "GET"])
@login_required
@isAdmin
def addHospital():
    form=AddHospital()
    if form.validate_on_submit():
        hospital = Hospital(name = form.name.data, city = form.city.data, address= form.address.data)
        db.session.add(hospital)
        db.session.commit()
        departments = form.departments.data
        for department in departments:
            hospitalDepartment = HospitalDepartments(hospital_id=hospital.id, department=department)
            db.session.add(hospitalDepartment)
        db.session.commit()
        days = form.visitingDays.data
        for day in days:
            hospitalDays = HospitalDaysToVisit(hospital_id=hospital.id, day=day)
            db.session.add(hospitalDays)
        db.session.commit()
        return redirect(url_for("hospitals"))
    return render_template("addHospital.html", form=form)


def remainingDaysF(days):
    remainingDays = Weekdays.getWeekdays()
    for day in days:
        if day in remainingDays:
            remainingDays.remove(day)
    return remainingDays

@app.route("/editHospital", methods=["POST", "GET"])
@login_required
@isAdmin
def editHospital():
    form = EditHospital()
    days = []
    if request.method == "POST":
        id = int(request.form.get("id"))
        if not id:
            return redirect("/home")
        hospital = Hospital.query.filter_by(id=id).first()
        form.hospital_id.data = id
        form.name.data = hospital.name
        form.city.data = hospital.city
        form.address.data = hospital.address
        allDepartments = Departments.query.all()
        remainingDepartments = []
        for department in allDepartments:
            remainingDepartments.append(department.name)
        hospitalDepartments = hospital.departments
        for hdepartment in hospitalDepartments:
            remainingDepartments.remove(hdepartment.department)
        hospitalDays = hospital.visitingDays
        days = []
        for day in hospitalDays:
            days.append(day.day)
        remainingDays = remainingDaysF(days)
        return render_template("updateHospital.html", sidebar=6, form=form, hospital=hospital, remainingDepartments=remainingDepartments, remainingDays=remainingDays)
    return redirect("/hospitals")

@app.route("/updateHospitalVisitingDays", methods=["POST"])
@login_required
@isAdmin
def updateHospitalVisitingDays():
    id = request.form.get("id")
    hospital = Hospital.query.filter_by(id=id).first()
    oldVisitingDays = hospital.visitingDays
    for day in oldVisitingDays:
        db.session.delete(day)
    db.session.commit()
    newVisitingDays = []
    for day in Weekdays.getWeekdays():
        checkDay = request.form.get(day)
        if checkDay:
            newVisitingDays.append(day)
    for day in newVisitingDays:
        vDay = HospitalDaysToVisit(day=day, hospital_id=id)
        db.session.add(vDay)
    db.session.commit()
    return redirect("/hospitals")


@app.route("/updateHospitalDepartments", methods=["POST"])
@login_required
@isAdmin
def updateHospitalDepartments():
    id = request.form.get("id")
    hospital = Hospital.query.filter_by(id=id).first()
    oldDepartments = hospital.departments
    for dpt in oldDepartments:
        db.session.delete(dpt)
    db.session.commit()
    allDepartments = []
    aDepartments = Departments.query.all()
    for department in aDepartments:
        allDepartments.append(department.name)
    for dpt in allDepartments:
        checkDepartment = request.form.get(dpt)
        if checkDepartment:
            hdepartment = HospitalDepartments(hospital_id=id, department=dpt)    
            db.session.add(hdepartment)
    db.session.commit()
    return redirect("/hospitals")

@app.route("/updateHospitalDetails", methods=["POST", "GET"])
@login_required
@isAdmin
def updateHospitalDetails():
    form=EditHospital()
    if form.validate_on_submit:
        hospital_id=form.hospital_id.data
        hospital = Hospital.query.filter_by(id=hospital_id).first()
        hospital.name = form.name.data.strip().lower().title()
        hospital.city = form.city.data
        hospital.address = form.address.data.strip()
        db.session.commit()
    return redirect("/hospitals")