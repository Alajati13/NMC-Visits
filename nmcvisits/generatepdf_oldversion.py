from fpdf import FPDF
import os
from flask import current_app


def generatePDF(userPhoto, appointment_id):
    pdf = FPDF(orientation = 'P', unit = 'mm', format = 'A4')
    pdf.add_page()
    pdf.set_font('Helvetica', size=24)
    pdf.set_text_color(90, 150, 255)

    path = os.path.join(current_app.root_path, "static/NMC_Logo.png")
    pdf.image(path, x = 30, y = 20, w = 30, h = 10)
    pdf.text(x = 78, y = 28, txt="NMC Hospital Visit Request")

    pdf.set_font('Helvetica', size=18)
    pdf.set_text_color(0, 0, 0)

    path = os.path.join(current_app.root_path, "static/Profile_Photos", userPhoto)
    pdf.image(path, x = 30, y = 100, w = 40, h = 40)

    pdf.set_xy(0, 50)
    pdf.cell(200, 15, txt = "Request for Visit", ln = 1, align = 'C')
    pdf.set_xy(0, 60)
    pdf.cell(200, 15, txt = "Date : 16/12/2022", ln = 1, align = 'C')

    pdf.set_xy(110, 80)
    pdf.cell(100, 15, txt = "Requester : Ali Alajati", ln = 1, align = 'l')
    pdf.set_xy(110, 90)
    pdf.cell(100, 15, txt = "Desidnation : Produc Specialist", ln = 1, align = 'l')
    pdf.set_xy(110, 100)
    pdf.cell(100, 15, txt = "Company : Bayer", ln = 1, align = 'l')
    pdf.set_xy(110, 110)
    pdf.cell(100, 15, txt = "Email : alajati13@hotmail.com", ln = 1, align = 'l')
    pdf.set_xy(110, 120)
    pdf.cell(100, 15, txt = "Phone : 0507553868", ln = 1, align = 'l')

    pdf.text(x = 10, y = 135, txt="______________________________________________________")

    # add photo of the user next to the text
    # generate qr code for link with key value pair at the end that opens only from a logged in admin showing the appointment is valid, and admin can click that appointment is used. if used already then cannot be used again.
    # add text at the end for like offical signature or stuff like that

    outputPath = os.path.join(current_app.root_path, "static/Visits_Printouts", appointment_id)
    pdf.output(outputPath)


