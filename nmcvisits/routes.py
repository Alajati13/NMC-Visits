from cgitb import html
import secrets
import os
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, send_from_directory
from sqlalchemy import true
from nmcvisits import app, db, bcrypt, mail
from nmcvisits.forms import RegistrationForm, LoginForm, UpdateProfileForm ,AddDepartments, CreateAppointment, UpdateVisitingDays, RequestResetForm, ResetPasswordForm
from nmcvisits.models import Departments, User, Appointment, AllowedDaysToVisit, VisitedDepartments
from flask_login import login_user, current_user, logout_user, login_required
from nmcvisits.helpers import getDepartments, getAllowedDaysToVisit, savePicture, generatePDF
from flask_mail import Message
import magic
from threading import Thread



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
def departments():
    departments = getDepartments()
    form = AddDepartments()
    if form.validate_on_submit():
        department = Departments(departmentName = form.department.data.strip().title())
        db.session.add(department)
        db.session.commit()
        return redirect(url_for("departments"))
    return render_template("departments.html", departments=departments, sidebar = 4, form=form)


@app.route("/deleteDepartment", methods=["POST"])
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
    return redirect(url_for("departments"))

def sendConfirmationEmail(user, appointment):
    msg = Message(subject = "Your Appointment to Visit NMC Hospital is Confirmed", sender = "alajati13@gmail.com", recipients=[user.email],
    body = "please print the attched pdf before proceeding to security office",
    html = f'''<h1>Hi {user.username}</h1>please print the attched pdf before proceeding to security office''')
    appointment_id = str(appointment.id)
    generatePDF(appointment_id)
    path = os.path.join(app.root_path, "static/Visits_Printouts")
    file = os.path.join(path, (str(appointment_id) + ".pdf"))
    fileName = "Confirmation"
    mime = magic.from_file(file, mime=True)
    with open(file, "rb") as fp: 
        msg.attach(filename=fileName, content_type = mime, data=fp.read(), disposition=None, headers=None)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


@app.route("/createAppointment", methods=["POST", "GET"])
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
        return redirect(url_for("createAppointment"))
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

@app.route("/deleteAppointment", methods=["POST", "GET"])
@login_required
def deleteAppointment():
    appointment_id = request.form.get("appointment_id")
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    rows = VisitedDepartments.query.filter_by(appointment_id=appointment_id).all()
    for row in rows:
        db.session.delete(row)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for("createAppointment"))


@app.route("/allowedDaysToVisit", methods=["POST", "GET"])
@login_required
def allowedDaysToVisit():
    form = None
    form = UpdateVisitingDays()
    if form.validate_on_submit():
        day = AllowedDaysToVisit(day=form.day.data) 
        db.session.add(day)
        db.session.commit()       
        return redirect(url_for("allowedDaysToVisit"))
    return render_template("allowedDaysToVisit.html", days = getAllowedDaysToVisit(), sidebar = 4, form=UpdateVisitingDays())

@app.route("/deleteDay", methods=["POST"])
@login_required
def deleteDay():
    dayName = request.form.get("day")
    day = AllowedDaysToVisit.query.filter_by(day=dayName).first()
    db.session.delete(day)
    db.session.commit()
    return redirect(url_for("allowedDaysToVisit"))

@app.route("/users", methods=["POST", "GET"])
@login_required
def users():
    users = User.query.all()
    return render_template("users.html", sidebar = False, users=users)

@app.route("/printAppointment", methods=["POST", "GET"])
@login_required
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
def allow(number):
    appointment = Appointment.query.filter_by(id=number).first()
    user = User.query.filter_by(id=appointment.visitor_id).first()
    departments_id = VisitedDepartments.query.filter_by(appointment_id=appointment.id).all()
    departments = []
    for dpt in departments_id:
        department = Departments.query.filter_by(id=dpt.department_id).first()
        departments.append(department.departmentName)
    return render_template("appointment.html", sidebar = 4, appointment=appointment, user=user, departments=departments)


@app.route("/appointments", methods=["POST", "GET"])
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

def sendResetEmail(user):
    token = user.get_reset_token()
    msg = Message(subject = "Password Reset Request", sender = "alajati13@gmail.com", recipients=[user.email],
    body = f'''To reset your password, visit the following link
{url_for("resetToken", token=token, _external=True)}
    
If you did not make this request then simply ignore this email and no changes will be made
''',
    html = f'''<h1>Hi {user.username}</h1>To reset your password, visit the following link
{url_for("resetToken", token=token, _external=True)}
    
<small>If you did not make this request then simply ignore this email and no changes will be made</small>
''')
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

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


"""
f'''To reset your password, visit the following link
{url_for("resetToken", token=token, _external=True)}
    
If you did not make this request then simply ignore this email and no changes will be made
'''
"""
