
import os
from PIL import Image
import secrets
import secrets
from flask import url_for, current_app
from flask_mail import Message
# from threading import Thread
# from nmcvisits.Appointments.helpers import send_async_email
from nmcvisits import mail

def sendResetEmail(user):
    token = user.get_reset_token()
    msg = Message(subject = "Password Reset Request", sender = "alajati13@gmail.com", recipients=[user.email],
    body = f'''To reset your password, visit the following link
{url_for("users.resetToken", token=token, _external=True)}
    
If you did not make this request then simply ignore this email and no changes will be made
''',
    html = f'''<h1>Hi {user.username}</h1>To reset your password, visit the following link
{url_for("users.resetToken", token=token, _external=True)}
    
<small>If you did not make this request then simply ignore this email and no changes will be made</small>
''')
    mail.send(msg) # to be deleted after tfixing the async issue
    #    thr = Thread(target=send_async_email, args=[current_app, msg])
    #    thr.start()

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
    picturePath = os.path.join(current_app.root_path, "static/Profile_Photos", pictureName)
    i = resizeImage(formPicture)
    i.save(picturePath)
    i.close()
    return pictureName

