from flask import redirect, render_template, flash, request, url_for, Blueprint, current_app
from flask_login import current_user, login_required, login_user, logout_user
from nmcvisits import db, bcrypt, login_manager, mail
from nmcvisits.models import User
from nmcvisits.Users.forms import LoginForm, RegistrationForm, UpdateProfileForm, ResetPasswordForm, RequestResetForm
from nmcvisits.Users.helpers import savePicture, sendResetEmail
import os



usersBP = Blueprint("users", __name__)


@usersBP.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            nextPage = request.args.get("next") 
            return redirect(nextPage) if nextPage else redirect(url_for("main.home"))
        else:
            flash("Login Unsuccesful. Please check email and password", "danger")
    return render_template("login.html", title = "Login", form=form)

@usersBP.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pasword = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username = form.username.data.strip().title(), email = form.email.data, password = hashed_pasword)
        db.session.add(user)
        db.session.commit()
    
        flash(f'Your account has been created. Please Log in and complete your profile data to proceed.', 'success')
        return redirect("/login")
    return render_template("register.html", title = "Register", form=form)    

@usersBP.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

# do profile so that it shows one view (no sidebar) and there is a big edit profile button that add sidebar with editing tools 
@usersBP.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateProfileForm() 
    if form.validate_on_submit():
        if form.picture.data:
            pictureFile = savePicture(form.picture.data)
            if current_user.imageFile != "default.jpg":
                oldPicturePath = os.path.join(current_app.root_path, "static/Profile_Photos", current_user.imageFile)
                os.remove(oldPicturePath)
            current_user.imageFile = pictureFile
        current_user.username = form.username.data.strip().title()
        current_user.jobTitle = form.jobTitle.data.strip().title()
        current_user.company = form.company.data.strip().title()
        current_user.phone = form.phone.data.strip()
        db.session.commit()
        flash("your profile has been updated", "success")
        return redirect(url_for("users.profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.jobTitle.data = current_user.jobTitle
        form.company.data = current_user.company
        form.phone.data = current_user.phone

    imageFile = url_for("static", filename="profile_photos/" + current_user.imageFile)
    return render_template("profile.html", title = "Profile", sidebar = 7, imageFile=imageFile, form=form)





@usersBP.route("/resetPassword", methods=["POST", "GET"])
def resetRequest():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendResetEmail(user)
        flash("An email has been sent with instruction to reset your password", "info")
        return redirect(url_for("users.login"))
    return render_template("resetrequest.html", title = "Reset Password", form=form)


@usersBP.route("/resetPassword/<token>", methods=["POST", "GET"])
def resetToken(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.resetrequest"))    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pasword = bcrypt.generate_password_hash(form.password.data).decode("utf-8")    
        user.password = hashed_pasword
        db.session.commit()
        flash(f'Your password has been updated. Yu are now able to Login', 'success')
        return redirect("/login")
    return render_template("resetToken.html", title = "Reset Password", form=form)

@usersBP.route("/users", methods=["POST", "GET"])
@login_required
def users():
    users = User.query.all()
    return render_template("users.html", sidebar = False, users=users)