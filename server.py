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
    """Confirm new account"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")
    user_phone = request.form.get("phone")

    confirmed_user = User.get_user_by_email(user_email)

    if not confirmed_user:
        User.create_new_user(user_email, user_password, user_phone)
        flash("You successfully created an account! Please log in to get started.")
    else:
        flash("You already have an account. Please sign in.")

    return redirect("/")


@app.route("/login")
def login_user():
    """Allow user to log into site."""

    return render_template("login.html")


@app.route("/login-confirm", methods=["POST"])
def confirm_user_login():
    """Confirm user account information is correct."""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    confirmed_user = User.validate_email_password(user_email, user_password)

    if confirmed_user:
        userid = confirmed_user.user_id
        session["User"] = userid
        return redirect("/myrecipes/%d" % userid)
    else:
        flash("Your email and password combination are not correct.")
        return redirect("/login")


@app.route("/logout")
def logout_user():
    """Log out the user"""

    del session['User']

    flash("You are logged out")

    return redirect("/")


@app.route("/myrecipes/<int:userid>")
def display_recipe_list(userid):
    """Display a list of recipes for a given user."""

    return render_template("recipe_list.html", userid=userid)


@app.route("/myrecipes/<int:userid>/addrecipe")
def create_new_recipe(userid):
    """Allow user to create a new recipe."""

    return render_template("new_recipe.html")


@app.route("/recipe-confirm", methods=["POST"])
def add_new_recipe():
    """Add new recipe to the database."""

    print request.form

    user_id = session['User']
    recipe_title = request.form.get("title")
    instructions = request.form.get("instructions")
    source = request.form.get("source")

    # hashtags = request.form.get("hashtags")
    # hashtag_list = [hashtags.strip("#") for hashtag in hashtags.split() if hashtag.startswith("#")]

    new_recipe = Recipe.create_new_recipe(user_id, recipe_title, instructions, source)
    recipe_id = new_recipe.recipe_id

    # new_ingredient = Ingredient(quantity=4, measure='tbsp', recipe_id=3, item='oil')

    # hashtag = Hashtag.filter_by(hashtag=Your_Form_Hashtag).first()
    # if hashtag:
    #         # this is already in the hashtag table
    #         rec_hash = RecipeHashtag()
    # else:
    #         # add new, get new one's id, pass into RecipeHashtag.create_new_rec_hash()
    #         new_rec_hash =

    return redirect("/myrecipes/%d" % user_id)

################################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
