from ssl import ALERT_DESCRIPTION_PROTOCOL_VERSION
from textwrap import wrap
from nmcvisits.models import User, Appointment, Departments, AllowedDaysToVisit # ,VisitedDepartments
from nmcvisits import db, app
import os
from PIL import Image, ImageOps
import secrets
from fpdf import FPDF

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

def notYetAllowedDays():
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    notYetAllowedDays = weekdays
    rows = AllowedDaysToVisit.query.all()
    for row in rows:
        notYetAllowedDays.remove(row.day)
    return notYetAllowedDays

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
    
def generatePDF(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    user_id = appointment.visitor_id
    user = User.query.filter_by(id=user_id).first()        
    userphoto = user.imageFile
    pdf = FPDF(orientation = 'P', unit = 'mm', format = 'A4')
    pdf.add_page()
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
    pdf.cell(100, 15, txt = f"Desidnation : {user.jobTitle}", ln = 1, align = 'l')
    pdf.set_xy(80, 100)
    pdf.cell(100, 15, txt = f"Company : {user.company} ", ln = 1, align = 'l')
    pdf.set_xy(80, 110)
    pdf.cell(100, 15, txt = f"Email : {user.email}", ln = 1, align = 'l')
    pdf.set_xy(80, 120)
    pdf.cell(100, 15, txt = f"Phone : {user.phone}", ln = 1, align = 'l')

    pdf.text(x = 10, y = 135, txt="______________________________________________________")

    # add photo of the user next to the text
    # generate qr code for link with key value pair at the end that opens only from a logged in admin showing the appointment is valid, and admin can click that appointment is used. if used already then cannot be used again.
    # add text at the end for like offical signature or stuff like that

    outputPath = os.path.join(app.root_path, "static/Visits_Printouts", (appointment_id + ".pdf"))
    pdf.output(outputPath)





    """
    def savePicture(formPicture):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(formPicture.filename)
    pictureName = random_hex + ext
    picturePath = os.path.join(app.root_path, "static/Profile_Photos", pictureName)
    outputSize = (400,400)
    i = Image.open(formPicture)
    i.thumbnail(outputSize)
    i.save(picturePath)
    i.close()
    return pictureName
    """