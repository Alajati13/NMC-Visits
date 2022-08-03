from nmcvisits.models import User, Appointment, Departments, VisitedDepartments
from nmcvisits import db, app, mail
import os
from PIL import Image, ImageOps
import secrets
from fpdf import FPDF
import qrcode   
import shutil
from functools import wraps
from flask_login import current_user
from flask import render_template, flash, url_for, redirect
from flask_mail import Message
from threading import Thread
import magic

def getDepartments():
    departments = []
    for row in Departments.query.all():
        departments.append(row.name)
        departments.sort()
    return departments

def resizeImage(path):
    im = Image.open(path)
    thumb_width = 400

    def crop_center(pil_img, crop_width, crop_height):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                            (img_height - crop_height) // 2,
                            (img_width + crop_width) // 2,
                            (img_height + crop_height) // 2))

    def crop_max_square(pil_img):
        return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    im_thumb = crop_max_square(im).resize((thumb_width, thumb_width), Image.Resampling.LANCZOS)

    return im_thumb

def savePicture(formPicture):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(formPicture.filename)
    pictureName = random_hex + ext
    picturePath = os.path.join(app.root_path, "static/Profile_Photos", pictureName)
    i = resizeImage(formPicture)
    i.save(picturePath)
    i.close()
    return pictureName

def generateQRcode(appointment_id):
    # Link for website
    baselink = "http://127.0.0.1:5000/appointment/"
    link = baselink + appointment_id
    #Creating an instance of qrcode
    qr = qrcode.QRCode(
        version=1,
        box_size=20,
        border=1)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    path = os.path.join(app.root_path, "static/Visits_Printouts", (appointment_id + ".png"))
    img.save(path)
        
def generatePDF(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    user_id = appointment.visitor_id
    user = User.query.filter_by(id=user_id).first()        
    userphoto = user.imageFile
    pdf = FPDF(orientation = 'P', unit = 'mm', format = 'A4')
    pdf.add_page()

    pdf.rect(2, 2, 206, 293, style = 'd')
    pdf.rect(3, 3, 204, 291, style = 'd')
    
    pdf.set_font('Helvetica', size=24)
    pdf.set_text_color(90, 150, 255)

    logo_path = os.path.join(app.root_path, "static/NMC_Logo.png")
    pdf.image(logo_path, x = 30, y = 20, w = 30, h = 10)
    pdf.text(x = 78, y = 28, txt="NMC Hospital Visit Request")

    pdf.set_font('Helvetica', size=18)
    pdf.set_text_color(0, 0, 0)

    path = os.path.join(app.root_path, "static/Profile_Photos", userphoto)
    img = Image.open(path)
    bordered_img = ImageOps.expand(img, border=4, fill = "green")
    save_path = os.path.join(app.root_path, userphoto)
    bordered_img.save(save_path)
    pdf.image(save_path, x = 15, y = 85, w = 45, h = 45)
    img.close()
    os.remove(save_path)

    pdf.set_xy(0, 50)
    pdf.cell(200, 15, txt = "Request for Visit", ln = 1, align = 'C')
    pdf.set_xy(0, 60)
    pdf.cell(200, 15, txt = f"Date : {appointment.appointmentDate.date()}", ln = 1, align = 'C')

    pdf.set_xy(80, 80)
    pdf.cell(100, 15, txt = f"Requester : {user.username}", ln = 1, align = 'l')
    pdf.set_xy(80, 90)
    pdf.cell(100, 15, txt = f"Job Title : {user.jobTitle}", ln = 1, align = 'l')
    pdf.set_xy(80, 100)
    pdf.cell(100, 15, txt = f"Company : {user.company} ", ln = 1, align = 'l')
    pdf.set_xy(80, 110)
    pdf.cell(100, 15, txt = f"Email : {user.email}", ln = 1, align = 'l')
    pdf.set_xy(80, 120)
    pdf.cell(100, 15, txt = f"Phone : {user.phone}", ln = 1, align = 'l')

    pdf.text(x = 10, y = 135, txt="______________________________________________________")

    pdf.set_xy(15, 140)
    pdf.cell(30, 10, txt = "Departments :", ln = 1, align = 'l')
    dpts = VisitedDepartments.query.filter_by(appointment_id=appointment_id).all()
    y = 150
    pdf.set_font('Helvetica', size=14)
    pdf.set_text_color(150, 150, 150)
    for department_id in dpts:
        department = Departments.query.filter_by(id=department_id.department_id).first()
        pdf.set_xy(15, y)
        pdf.cell(30, 10, txt = f"- {department.name}", ln = 1, align = 'l')
        y += 10
    # add text at the end for like offical signature or stuff like that
    generateQRcode(appointment_id)
    qr_path = os.path.join(app.root_path, "static/Visits_Printouts", (appointment_id + ".png"))
    pdf.image(qr_path, x = 70, y = 140, w = 120, h = 120)
    os.remove(qr_path)
    outputPath = os.path.join(app.root_path, "static/Visits_Printouts", (appointment_id + ".pdf"))
    pdf.output(outputPath)

def isAdmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "Admin":
            flash("You need to be logged in as Admin to access the requested page!","info")
            return render_template("home.html", title = "Access not allowed")
        return f(*args, **kwargs)
    return decorated_function


def isProfileComplete(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        userDetails = {}
        userDetails["Full Name"]=current_user.username
        userDetails["JobT itle"]=current_user.jobTitle
        userDetails["Company"]=current_user.company
        userDetails["Phone"]=current_user.phone
        isComplete = True
        missingElements = []
        for element in userDetails:
            if userDetails[element] == None:
                isComplete = False
                missingElements.append(element)
        if current_user.imageFile == "default.jpg":
            missingElements.append("Image File")
            isComplete = False
        if not isComplete:
            flash(f"You need to complete your profile to be able to request appointments. Missing Details : {missingElements}","info")
            return redirect("/profile")
        return f(*args, **kwargs)
    return decorated_function


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

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

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