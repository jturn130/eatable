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

    ###### Recipe Table Section ######
    user_id = session['User']
    recipe_title = request.form.get("title")
    instructions = request.form.get("instructions")
    source = request.form.get("source")

    new_recipe = Recipe.create_new_recipe(user_id, recipe_title, instructions, source)
    recipe_id = new_recipe.recipe_id

    ###### Ingredient Table Section ######
    count = 0

    # use count to find the number of ingredients
    # the loop looks for "item" because that's a required field
    for r in request.form:
        if r[0][0:4] == 'item':
            count += 1
    print count

    ingredients_to_add = {}

    for i in range(1, (count+1)):
        #the range refers to the range of integers that appear in the ingredient names
        ingredients_to_add[i] = []
        for r in request.form:
            # looks for entries that end with an integer
            if r[0][0:3] == 'ite' or r[0][0:3] == 'pre' or r[0][0:3] == 'mea' or r[0][0:3] == 'qty':

                # checks if the last character of an entry equals the integer we're using
                # if yes, takes that entry and converts it into a list
                # appends that entry to the corresponding value in our ingredients dictionary
                # sorts the value so we know how to index the list later
                last_char = int(r[0][-1])
                if last_char == i:
                    r = list(r)
                    ingredients_to_add[i].append(r)
                    ingredients_to_add[i].sort()

        # creates a new list of ingredients
        # takes out the ingredient heading and unnecessary nested lists
        # (this is because we just want the actual text)
        # appends cleaned up ingredient info to a new list
        # sets new list as the new value in the corresponding dict key
        new_ingredient_list = []
        for x in ingredients_to_add[i]:

            del x[0]
            for y in x:
                x = y
                new_ingredient_list.append(x)

        ingredients_to_add[i] = new_ingredient_list
    print "this is the ingredients dict: %s" % ingredients_to_add

    # Within the value list of a dict entry, the indexes mean:
    # 0 = item
    # 1 = measure
    # 2 = prepnotes
    # 3 = qty
    for i in range(1, (count+1)):
        item = ingredients_to_add[i][0]
        measure = ingredients_to_add[i][1]
        prepnotes = ingredients_to_add[i][2]
        qty = ingredients_to_add[i][3]

        Ingredient.add_ingredient_to_recipe(recipe_id, item, qty, measure, prepnotes)

    ###### Hashtag & Recipe_Hashtag Table Section ######
    hashtags = request.form.get("hashtags")
    hashtag_list = [hashtag.strip("#") for hashtag in hashtags.split() if hashtag.startswith("#")]

    for hashtag in hashtag_list:

        #checks if the hashtag already exists in db
        old_hashtag = Hashtag.check_if_hashtag_exists(hashtag)

        #if yes, then we get the hashtag_id from the old hashtag
        if old_hashtag:
            hashtag_id = old_hashtag.hashtag_id

        #if no, we create a new hashtag, then get the hastag_id from it
        else:
            new_hashtag = Hashtag.create_new_hashtag(hashtag)
            hashtag_id = new_hashtag.hashtag_id

        #takes the given recipe_id and hashtag_id and create a recipe_hashtag
        Recipe_Hashtag.create_new_recipe_hashtag(recipe_id, hashtag_id)

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
