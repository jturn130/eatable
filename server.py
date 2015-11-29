from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify

from flask_debugtoolbar import DebugToolbarExtension

import json

import re

import os

from twilio.rest import TwilioRestClient

import twilio.twiml

from passlib.hash import sha256_crypt

from model import User, Recipe, Ingredient, Recipe_Hashtag, Hashtag, Cart_Ingredient, Cart, connect_to_db, db

from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raises an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined

##########################################################################
# API Classes


class IdentifyUser(Resource):
    def get(self, email):
        """Get a user's userid given their email address."""

        user = User.get_user_by_email(email)

        return {user.user_id: user.email}


class UserRecipe(Resource):
    def get(self, userid):
        """Get a list of user recipes. Returns JSON as {recipe_id: recipe_title}."""

        user_recipes = Recipe.get_user_recipe_list(userid)

        recipes_dict = {}

        for r in user_recipes:
            recipes_dict[r[0]] = r[1]
        return recipes_dict


class UserIngredient(Resource):
    def get(self, userid):
        """
        Get a list of user ingredients and the number of times they appear
        in a user's recipes.

        Returns JSON as {ingredient_name: count}
        """

        user_ings = Ingredient.get_ingredient_counts_by_user(userid)

        ingredients_dict = {}

        for i in user_ings:
            ingredients_dict[i[0]] = i[1]

        return ingredients_dict


class UserHashtag(Resource):
    def get(self, userid):
        """Get a list of all of a user's hashtags."""

        user_tags = Hashtag.get_hashtags_by_user(userid)

        tags_list = [t[0] for t in user_tags]

        return {'hashtags': tags_list}


class Search(Resource):
    def get(self, query):
        """
        Get a list of relevant recipes given a query.

        Returns JSON as {recipe id: [recipe title, relevance ranking]}
        """

        search_results = Recipe.run_api_search_query(query)

        search_dict = {}

        for s in search_results:
            search_dict[s[0]] = [s[1], s[2]]

        return search_dict

api.add_resource(IdentifyUser, '/api/users/<string:email>')
api.add_resource(Search, '/api/recipes/search/<string:query>')
api.add_resource(UserRecipe, '/api/recipes/<int:userid>')
api.add_resource(UserIngredient, '/api/ingredients/<int:userid>')
api.add_resource(UserHashtag, '/api/hashtags/<int:userid>')

##########################################################################
# Routes


@app.route("/developers")
def display_developer_info():
    """Learn about the eatable API."""

    return render_template("api.html")


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/signup')
def create_account():
    """Sign up for an account"""

    return render_template("signup.html")


@app.route('/signup-confirm', methods=["POST"])
def confirm_new_account():
    """Confirm new account"""

    user_email = request.form.get("email")
    user_password = request.form.get("password1")
    user_phone = request.form.get("phone")

    confirmed_user = User.get_user_by_email(user_email)

    if not confirmed_user:
        hash = sha256_crypt.encrypt(user_password)
        User.create_new_user(user_email, hash, user_phone)
        flash("You successfully created an account! Please log in to get started.", "create_account")
    else:
        flash("You already have an account. Please sign in.", "account_already")

    return redirect("/")


@app.route("/login-confirm", methods=["POST"])
def confirm_user_login():
    """Confirm user account information is correct."""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    try:
        # checks if user exists
        user = User.get_user_by_email(user_email)

        # get pw from db and compare it to user input
        hash = user.password

        password_check = sha256_crypt.verify(user_password, hash)

        # if everything works, log user in and create a cart
        if password_check:

            userid = user.user_id
            session['User'] = userid

            if 'Cart' not in session:
                    new_cart = Cart.create_new_cart(userid)
                    session['Cart'] = new_cart.cart_id

            return jsonify({"confirmed_user": True, "user_id": userid})
        else:
            raise Exception

    except Exception:
        return jsonify({"confirmed_user": False})


@app.route("/logout")
def logout_user():
    """Log out the user."""

    del session['User']
    del session['Cart']

    flash("You are logged out.", "logged_out")

    return redirect("/")


@app.route("/editprofile/<int:userid>")
def display_edit_profile_options(userid):
    """Get user info and display it so user can edit."""

    editeduser = User.get_user_by_id(userid)

    return render_template("edit_profile.html", editeduser=editeduser)


@app.route("/edit-profile-confirm/<int:userid>", methods=["POST"])
def confirm_profile_edits(userid):
    """Update the db to reflect user changes to profile."""

    # Gets form data
    user_email = request.form.get("email")
    user_password = request.form.get("password1")
    user_phone = request.form.get("phone")

    # Check if user changed password
    if user_password and user_password != "":
        # If yes, hashes password
        hash = sha256_crypt.encrypt(user_password)

        # Updates the db
        User.update_user_and_pw(userid, user_email, hash, user_phone)
    else:
        # If no, updates everything else
        User.update_user(userid, user_email, user_phone)

    flash("Your profile edits have been saved", "edit_profile")

    return redirect("/myrecipes/%d" % userid)


@app.route("/myrecipes/<int:userid>")
def display_recipe_list(userid):
    """Display a list of recipes for a given user."""

    user_recipes = Recipe.get_user_recipe_list(userid)

    return render_template("recipe_list.html", userid=userid, user_recipes=user_recipes)


@app.route("/myrecipes/<int:userid>/searchresults", methods=["GET"])
def get_search_results(userid):
    """Run search query and return results."""

    search_query = request.args.get("searchQuery")

    if search_query != '':
        ##returns list of tuples
        ##index[0] = recipe_id
        ##index[1] = recipe_title
        ##index[2] = rank
        search_recipes = Recipe.run_search_query(userid, search_query)

    else:
        #gets all user recipes if the search query field is blank
        search_recipes = Recipe.get_user_recipe_list(userid)

    #creates dictionary from search results
    #key = recipeid
    #value = {dictionary of recipe title and userid}
    recipes_list = []

    for recipe in search_recipes:
        recipe = list(recipe)
        recipes_list.append(recipe)

    return json.dumps(recipes_list)


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>")
def display_recipe(userid, recipeid):
    """Retrieves an individual recipe from db for display."""

    recipe = Recipe.get_recipe(recipeid)

    ingredients = Ingredient.get_recipe_ingredients(recipeid)

    recipe_hashtags = Recipe_Hashtag.get_recipe_hashtags(recipeid)

    return render_template("recipe_info.html", recipe=recipe,
                           ingredients=ingredients, recipe_hashtags=recipe_hashtags,
                           userid=userid)


@app.route("/typeahead")
def get_suggestions():
    """Get user data for typeahead suggestions."""

    userid = session['User']

    #### Hashtag Data ####
    hashtag_data = Hashtag.get_hashtags_by_user(userid)
    hashtag_list = [h[0] for h in hashtag_data]

    #### Recipe Data ####
    recipe_data = Recipe.get_user_recipe_list(userid)
    recipe_list = [r[1] for r in recipe_data]

    #### Ingredient Data ####
    ingredient_data = Ingredient.get_ingredients_by_user(userid)
    # convert to set then back to list to remove duplicates
    ingredient_list = list(set([i[0] for i in ingredient_data]))

    #### Combined Data ####
    data_list = hashtag_list + recipe_list + ingredient_list

    return jsonify({"userdata": data_list})


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>/delete")
def delete_recipe(userid, recipeid):
    """Delete recipe from the db."""

    #delete old recipe_hashtags
    Recipe_Hashtag.delete_old_recipe_hashtags(recipeid)

    #delete old ingredients
    Ingredient.delete_old_recipe_ingredients(recipeid)

    #delete old recipe
    Recipe.delete_recipe(recipeid)

    #flash message
    flash("You have successfully deleted your recipe.", "delete_recipe")

    return redirect("/myrecipes/%d" % userid)


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>/edit")
def edit_recipe(userid, recipeid):
    """Get a recipe from the db, and display it so the user can edit."""

    recipe = Recipe.get_recipe(recipeid)

    ingredients = Ingredient.get_recipe_ingredients(recipeid)

    recipe_hashtags = Recipe_Hashtag.get_recipe_hashtags(recipeid)

    hashtag_list = Recipe_Hashtag.get_hashtag_names_for_recipe(recipe_hashtags)

    readable_hashtags = Hashtag.get_readable_hashtags(hashtag_list)

    recreated_hashtag_input = Hashtag.recreate_hashtag_input(readable_hashtags)

    return render_template("edit_recipe.html", recipe=recipe, ingredients=ingredients,
                           userid=userid, recreated_hashtag_input=recreated_hashtag_input)


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>/edit-confirm", methods=["POST"])
def confirm_recipe_edit(userid, recipeid):
    """Make changes to the db to reflect the recipe edits."""

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
    hashtag_list = re.sub('#', '', hashtags.lower()).split()

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

    flash("You have successfully edited your recipe.", "edit_recipe")

    return redirect("/myrecipes/%d/recipe/%d" % (userid, recipeid))


@app.route("/myrecipes/<int:userid>/addrecipe")
def create_new_recipe(userid):
    """Allow user to create a new recipe."""

    return render_template("new_recipe.html", userid=userid)


@app.route("/recipe-confirm", methods=["POST"])
def add_new_recipe():
    """Add new recipe to the database."""

    try:
        ###### Recipe Table Section ######
        user_id = session['User']
        recipe_title = request.form.get("recipetitle")
        instructions = request.form.get("instructions")
        source = request.form.get("recipesource")

        new_recipe = Recipe.create_new_recipe(user_id, recipe_title, instructions, source)
        recipe_id = new_recipe.recipe_id

        ###### Ingredient Table Section ######
        new_ingredient_count = Ingredient.get_ingredient_count(request.form)
        ingredients_dict = Ingredient.get_ingredients_to_add(new_ingredient_count, request.form)
        Ingredient.add_ingredient_to_recipe(new_ingredient_count, ingredients_dict, recipe_id)

        ###### Hashtag Table Section ######
        hashtags = request.form.get("hashtags")

        # stardardizes format for hashtags
        hashtag_list = re.sub('#', '', hashtags.lower()).split()

        hashtag_id_list = Hashtag.get_hashtag_id(hashtag_list)

        ###### Recipe_Hashtag Table Section ######
        Recipe_Hashtag.create_new_recipe_hashtag(recipe_id, hashtag_id_list)

        ###### Tsvector Generation ######
        Recipe.update_search_vector(recipe_id)

        flash("You have successfully created your recipe. Hooray!", "create_recipe")

        return redirect("/myrecipes/%d" % user_id)

    except Exception:

        return redirect("/")


@app.route("/myrecipes/<int:userid>/recipe/<int:recipeid>/addtocart")
def add_recipe_to_cart(recipeid, userid):
    """Add ingredients from a given recipe to grocery cart."""

    recipe_ingredients = Ingredient.get_recipe_ingredients(recipeid)

    for ingredient in recipe_ingredients:
        Cart_Ingredient.create_new_cart_ingredient(session['Cart'], ingredient.ingredient_id)

    flash("You have successfully added your recipe to your grocery cart.", "cart_add")

    return redirect("/myrecipes/%d/cart/%d" % (userid, session['Cart']))


@app.route("/myrecipes/<int:userid>/cart/<int:cartid>")
def display_cart(userid, cartid):
    """Display items in a user's cart."""

    cart_ings = Cart_Ingredient.get_cart_ingredients(cartid)

    return render_template("cart.html", userid=userid, cart_ings=cart_ings)


@app.route("/myrecipes/<int:userid>/cart/<int:cartid>/editcart")
def edit_cart(userid, cartid):
    """Display form fields so user can edit their cart."""

    cart_ings = Cart_Ingredient.get_cart_ingredients(cartid)

    return render_template("edit_cart.html", userid=userid, cart_ings=cart_ings)


@app.route("/myrecipes/<int:userid>/cart/<int:cartid>/edit-confirm", methods=["POST"])
def update_edited_cart(userid, cartid):
    """Update the cart_ingredients table to reflect edited changes."""

    # delete old cart ingredients
    Cart_Ingredient.delete_old_cart_ingredients(cartid)

    # get and format the new cart ingredients
    edited_cart_ings = Ingredient.get_edited_cart_ings(request.form)

    # add new cart ingredients to the ingredients table and cart_ingredients table
    Ingredient.add_edited_cart_ings_to_db(edited_cart_ings, cartid)

    return redirect("/myrecipes/%d/cart/%d" % (userid, cartid))


@app.route("/myrecipes/<int:userid>/cart/<int:cartid>/deletecart")
def delete_cart(userid, cartid):
    """Create new cart and reassign session cart."""

    # create new cart
    new_cart = Cart.create_new_cart(userid)

    # update session info to reflect new cart
    session['Cart'] = new_cart.cart_id

    flash("You successfully deleted your cart. Parting is such sweet sorrow.", "delete_cart")

    return redirect("/myrecipes/%d/cart/%d" % (session['User'], session['Cart']))


@app.route("/sms")
def send_text():
    """Send a SMS with user grocery cart."""

    # gets the phone number we're sending a text to
    user_phone = User.get_user_phone(session['User'])
    user_phone = "+1" + (str(user_phone))

    # gets the ingredients in the cart
    cart_ings = Cart_Ingredient.get_cart_ingredients(session['Cart'])

    cart_text = "My Cart:"

    # formats the cart ingredients
    for c in cart_ings:
        if c.ingredient.measure is None and c.ingredient.quantity is not None:
            cart_text += '\n + ' + c.ingredient.quantity + ' ' + c.ingredient.item
        else:
            cart_text += '\n + ' + c.ingredient.item

    #sends text via twilio
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = TwilioRestClient(account_sid, auth_token)

    message = client.messages.create(to=user_phone, from_=os.environ['TWILIO_NUMBER'],
                                     body=cart_text)

    resp = twilio.twiml.Response()
    resp.sms(message)

    flash("Your grocery cart was texted to you. Happy shopping!", "text_message")

    return redirect("/myrecipes/%d" % session['User'])


################################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
