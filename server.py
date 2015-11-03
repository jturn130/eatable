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

    user_recipes = Recipe.get_user_recipe_list(userid)

    return render_template("recipe_list.html", userid=userid, user_recipes=user_recipes)


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>")
def display_recipe(userid, recipeid):

    recipe = Recipe.get_recipe(recipeid)

    ingredients = Ingredient.get_recipe_ingredients(recipeid)

    recipe_hashtags = Recipe_Hashtag.get_recipe_hashtags(recipeid)

    return render_template("recipe_info.html", recipe=recipe, ingredients=ingredients, recipe_hashtags=recipe_hashtags, userid=userid)


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>/delete")
def delete_recipe(userid, recipeid):

    #delete old recipe_hashtags
    Recipe_Hashtag.delete_old_recipe_hashtags(recipeid)

    #delete old ingredients
    Ingredient.delete_old_recipe_ingredients(recipeid)

    #delete old recipe
    Recipe.delete_recipe(recipeid)

    #flash message
    flash("You have successfully delete your recipe.")

    return redirect("/myrecipes/%d" % userid)


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>/edit")
def edit_recipe(userid, recipeid):

    recipe = Recipe.get_recipe(recipeid)

    ingredients = Ingredient.get_recipe_ingredients(recipeid)

    recipe_hashtags = Recipe_Hashtag.get_recipe_hashtags(recipeid)

    hashtag_list = Recipe_Hashtag.get_hashtag_names_for_recipe(recipe_hashtags)

    readable_hashtags = Hashtag.get_readable_hashtags(hashtag_list)

    recreated_hashtag_input = Hashtag.recreate_hashtag_input(readable_hashtags)

    return render_template("edit_recipe.html", recipe=recipe, ingredients=ingredients, userid=userid, recreated_hashtag_input=recreated_hashtag_input)


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>/edit-confirm", methods=["POST"])
def confirm_recipe_edit(userid, recipeid):

    ####### Change Recipes Table ######
    recipe_title = request.form.get("recipetitle")
    instructions = request.form.get("instructions")
    source = request.form.get("source")

    #update recipe table
    Recipe.edit_recipe(recipeid, recipe_title, instructions, source)

    ###### Change Tngredients Table ######

    #delete old ingredients
    Ingredient.delete_old_recipe_ingredients(recipeid)

    #add new ingredients
    new_ingredient_count = Ingredient.get_ingredient_count(request.form)
    ingredients_dict = Ingredient.get_ingredients_to_add(new_ingredient_count, request.form)
    Ingredient.add_ingredient_to_recipe(new_ingredient_count, ingredients_dict, recipeid)

    ###### Change Hashtag Table ######

    # no need to delete from hashtags table
    # just need to delete from the recipe_hashtags association table
    hashtags = request.form.get("hashtags")
    hashtag_list = [hashtag.strip("#") for hashtag in hashtags.split() if hashtag.startswith("#")]

    # will add another row in hashtags table if a new hashtag
    # will get the hashtag_id if the hashtag already exists
    hashtag_id_list = Hashtag.get_hashtag_id(hashtag_list)

    ###### Recipe_Hashtag Table Section ######

    #delete old recipe_hashtags
    Recipe_Hashtag.delete_old_recipe_hashtags(recipeid)

    # generate new recipe_hashtags
    Recipe_Hashtag.create_new_recipe_hashtag(recipeid, hashtag_id_list)

    ###### Tsvector Generation ######
    Recipe.update_search_vector(recipeid)

    return redirect("/myrecipes/%d/recipe/%d" % (userid, recipeid))


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
    recipe_title = request.form.get("recipetitle")
    instructions = request.form.get("instructions")
    source = request.form.get("source")

    new_recipe = Recipe.create_new_recipe(user_id, recipe_title, instructions, source)
    recipe_id = new_recipe.recipe_id

    ###### Ingredient Table Section ######
    new_ingredient_count = Ingredient.get_ingredient_count(request.form)
    ingredients_dict = Ingredient.get_ingredients_to_add(new_ingredient_count, request.form)
    Ingredient.add_ingredient_to_recipe(new_ingredient_count, ingredients_dict, recipe_id)

    ###### Hashtag Table Section ######
    hashtags = request.form.get("hashtags")
    hashtag_list = [hashtag.strip("#") for hashtag in hashtags.split() if hashtag.startswith("#")]

    hashtag_id_list = Hashtag.get_hashtag_id(hashtag_list)

    ###### Recipe_Hashtag Table Section ######
    Recipe_Hashtag.create_new_recipe_hashtag(recipe_id, hashtag_id_list)

    ###### Tsvector Generation ######
    Recipe.update_search_vector(recipe_id)

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
