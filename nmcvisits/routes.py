from flask import render_template, url_for, redirect, flash
from nmcvisits import app
from nmcvisits.forms import RegistrationForm, LoginForm
from nmcvisits.models import User, Appointment


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title = "Home",)

@app.route("/about")
def about():
    return render_template("about.html", title = "About",)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Logged in as {form.email.data}!', 'success')
        return redirect("/home")
    return render_template("login.html", title = "Login", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect("/login")
    return render_template("register.html", title = "Register", form=form)    
