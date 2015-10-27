from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Recipe, Ingredient, Recipe_Hashtag, Hashtag, Cart_Ingredient, Cart, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raises an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/signup')
def create_account():
    """Sign up for an account"""

    return render_template("signup.html")


@app.route('/signup-confirm', methods=["POST"])
def confirm_account():
    """Confirms new account"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")
    user_phone = request.form.get("phone")

    confirmed_user = User.get_user_by_email(user_email)

    if not confirmed_user:
        User.create_user_by_email_password(user_email, user_password, user_phone)
        flash("You successfully created an account! Please log in to get started.")
    else:
        flash("You already have an account. Please sign in.")

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
