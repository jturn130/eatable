"""Models and database functions for Eatable."""

from flask_sqlalchemy import SQLAlchemy

# Connection to the SQLite database via the Flask-SQLAlchemy helper library
# On this, we can find the `session` object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions


############ User class ############
class User(db.Model):
    """User of Eatable."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    mobile_phone = db.Column(db.String(30), nullable=True)

    @classmethod
    def get_user_by_email(cls, user_email):
        """Use to see if an account with a given email address already exists."""

        try:
            user_login_info = User.query.filter_by(email=user_email).one()

            return user_login_info

        except Exception, error:
            print error

    @classmethod
    def create_new_user(cls, user_email, user_password, user_phone):
        """Add a new user to the database."""

        new_user = User(email=user_email, password=user_password, mobile_phone=user_phone)

        db.session.add(new_user)
        db.session.commit()

        print "Successfully added new user with the email: %s" % user_email

    @classmethod
    def delete_user(cls, user_email):
        """Delete a user from the db."""

        User.query.filter_by(email=user_email).delete()

        db.session.commit()

        print "Successfully deleted user with the email: %s!" % user_email

    @classmethod
    def get_user_phone(cls, userid):
        """Get user phone number given user id."""

        user = User.query.filter_by(user_id=userid).one()

        user_phone = user.mobile_phone

        return user_phone

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%d email=%s phone=%s>" % (self.user_id, self.email, self.mobile_phone)


############ Recipe class ############
class Recipe(db.Model):
    """Eatable recipe for a given user."""

    __tablename__ = "recipes"
    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipe_title = db.Column(db.String(150), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    source = db.Column(db.Text, nullable=True)

    @classmethod
    def create_new_recipe(cls, user_id, recipe_title, instructions, source=''):
        """Add a new recipe to the database."""

        new_recipe = Recipe(user_id=user_id, recipe_title=recipe_title, instructions=instructions, source=source)

        db.session.add(new_recipe)
        db.session.commit()

        return new_recipe

    @classmethod
    def update_search_vector(cls, recipeid):
        """Adds a a ranked tsvector for recipe."""

        QUERY = """
        UPDATE recipes SET searchdata = setweight(to_tsvector(coalesce(tags_line, '')), 'A')
        || setweight(to_tsvector(coalesce(raw_Search.recipe_title, '')), 'B') ||
        setweight(to_tsvector(coalesce(item_line, '')), 'C')
        FROM raw_Search WHERE raw_Search.recipe_id = recipes.recipe_id
        """

        db.session.execute(QUERY)
        db.session.commit()

        recipe = Recipe.query.filter_by(recipe_id=recipeid).one()
        return recipe

    @classmethod
    def run_search_query(cls, userid, searchquery):
        """Get relevant recipes given search query."""

        QUERY = """
        SELECT recipe_id, recipe_title, ts_rank(searchdata, to_tsquery('english', :searchquery)) as rank FROM recipes
        WHERE user_id = :userid AND searchdata @@ to_tsquery('english', :searchquery)
        ORDER BY rank DESC
        """

        cursor = db.session.execute(QUERY, {'userid': userid, 'searchquery': searchquery})
        search_recipes = cursor.fetchall()

        return search_recipes

    @classmethod
    def get_user_recipe_list(cls, userid):
        """Get all recipes added by a given user."""

        QUERY = """
        SELECT recipe_id, recipe_title FROM recipes WHERE user_id = :userid ORDER BY recipe_title
        """

        cursor = db.session.execute(QUERY, {'userid': userid})

        user_recipes = cursor.fetchall()

        return user_recipes

    @classmethod
    def get_recipe(cls, recipeid):
        """Get a recipe given the recipeid."""

        recipe = Recipe.query.filter_by(recipe_id=recipeid).one()

        return recipe

    @classmethod
    def edit_recipe(cls, recipeid, recipe_title, instructions, source=''):
        """Update the DB to reflect changes in recipe."""

        recipe_to_edit = Recipe.query.filter_by(recipe_id=recipeid).one()

        recipe_to_edit.recipe_title = recipe_title
        recipe_to_edit.instructions = instructions
        recipe_to_edit.source = source

        db.session.commit()
        return recipe_to_edit

    @classmethod
    def delete_recipe(cls, recipeid):
        """Deletes a recipe from the DB."""

        deleted_recipe = Recipe.query.filter_by(recipe_id=recipeid).delete()

        db.session.commit()
        return deleted_recipe

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Recipe recipe_id=%d user_id=%d recipe_title=%s instructions=%s>" % (self.recipe_id, self.user_id, self.recipe_title, self.instructions)


############ Ingredient class ############
class Ingredient(db.Model):
    """Individual ingredient information for a given recipe."""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=True)
    quantity = db.Column(db.String(10), nullable=True)
    measure = db.Column(db.String(50), nullable=True)
    item = db.Column(db.String(75), nullable=False)
    prep_notes = db.Column(db.String(150), nullable=True)

    @classmethod
    def get_ingredient_count(cls, requestform):
        """Find number of ingredients from input form."""

        count = 0
        for r in requestform:
            if r[0:4] == 'item':
                count += 1
        return count

    @classmethod
    def get_ingredients_to_add(cls, new_count, requestform):
        """Return a dict of ingredient properties."""

        ingredients_to_add = {}

        for i in range(1, (new_count+1)):
            #the range refers to the range of integers that appear in the ingredient names
            ingredients_to_add[i] = []
            for r in requestform:

                # looks for entries that end with an integer
                if r[0:3] == 'ite' or r[0:3] == 'pre' or r[0:3] == 'mea' or r[0:3] == 'qty':

                    # checks if the last character(s) of an entry equals the integer we're using
                    # if yes, appends key value pair in our ingredients dictionary
                    # sorts the value so we know how to index the list later

                    try:
                        int(r[-2:])
                        if int(r[-2:]) == i:
                            ingredients_to_add[i].append([r, requestform[r]])
                            ingredients_to_add[i].sort()
                    except Exception:
                        if int(r[-1]) == i:
                            ingredients_to_add[i].append([r, requestform[r]])
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
        return ingredients_to_add

    @classmethod
    def add_ingredient_to_recipe(cls, new_count, ingredients_dict, recipe_id):
        """Add ingredients in given recipe to the database."""

        for i in range(1, (new_count+1)):
            item = ingredients_dict[i][0]
            measure = ingredients_dict[i][1]
            prepnotes = ingredients_dict[i][2]
            qty = ingredients_dict[i][3]

            new_ingredient = Ingredient(recipe_id=recipe_id, item=item, quantity=qty,
                                        measure=measure, prep_notes=prepnotes)

            db.session.add(new_ingredient)
            db.session.commit()
        print "You successfully added ingredients!"

    @classmethod
    def get_edited_cart_ings(cls, form):
        """Get edited ingredients in a user's cart."""

        ings_dict = {}

        for r in form:
            try:
                i = int(r[-2:])
                if i in ings_dict:
                    ings_dict[i].append([r, form[r]])
                else:
                    ings_dict[i] = [[r, form[r]]]
            except Exception:
                i = int(r[-1:])
                if i in ings_dict:
                    ings_dict[i].append([r, form[r]])
                else:
                    ings_dict[i] = [[r, form[r]]]
            ings_dict[i].sort()

        ings_to_add = ings_dict.values()

        return ings_to_add

    @classmethod
    def add_edited_cart_ings_to_db(cls, ings_to_add, cartid):
        """Add edited cart ingredients to db."""

        for i in range(0, (len(ings_to_add))):

            item = ings_to_add[i][0][1]

            try:
                qty = int(ings_to_add[i][1][1])
                new_ing = Ingredient(item=item, quantity=qty)
            except Exception:
                new_ing = Ingredient(item=item)

            db.session.add(new_ing)
            db.session.commit()

            new_cart_ing = Cart_Ingredient(ingredient_id=new_ing.ingredient_id, cart_id=cartid)

            db.session.add(new_cart_ing)
            db.session.commit()

        return ings_to_add

    @classmethod
    def get_recipe_ingredients(cls, recipeid):
        """Get a list of ingredients in a given recipe."""

        recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipeid).all()

        return recipe_ingredients

    @classmethod
    def delete_old_recipe_ingredients(cls, recipeid):
        """Delete existing recipe ingredients."""

        deleted_ingredients = Ingredient.query.filter_by(recipe_id=recipeid).delete()

        return deleted_ingredients

    @classmethod
    def get_ingredients_by_user(cls, userid):
        """Get a list of ingredients that a user has inputted in all their recipes."""

        QUERY = """
        SELECT item
        FROM ingredients
        WHERE recipe_id IN (SELECT recipe_id FROM recipes WHERE user_id= :userid)
        """

        cursor = db.session.execute(QUERY, {'userid': userid})
        ingredients = cursor.fetchall()

        return ingredients

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Ingredient ingredient_id=%d recipe_id=%s quantity=%s measure=%s item=%s prep_notes=%s>" % (self.ingredient_id, self.recipe_id, self.quantity, self.measure, self.item, self.prep_notes)


############ Recipe_Hashtag class ############
class Recipe_Hashtag(db.Model):
    """Associates a hashtag with a specific recipe."""

    __tablename__ = "recipe_hashtags"

    recipe_hashtag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtags.hashtag_id'), nullable=False)

    hashtags = db.relationship('Hashtag')

    @classmethod
    def create_new_recipe_hashtag(cls, recipe_id, hashtag_id_list):
        """Iterates through list of hashtag_ids and adds to recipe_hashtags table."""

        for hashtag_id in hashtag_id_list:

            new_recipe_hashtag = Recipe_Hashtag(recipe_id=recipe_id, hashtag_id=hashtag_id)

            db.session.add(new_recipe_hashtag)
            db.session.commit()

    @classmethod
    def get_recipe_hashtags(cls, recipeid):
        """Get the recipe_hashtags given the recipe_id."""

        recipe_hashtags = Recipe_Hashtag.query.filter_by(recipe_id=recipeid).all()
        return recipe_hashtags

    @classmethod
    def get_hashtag_names_for_recipe(cls, recipe_hashtags):
        """Get a list of hashtag names given the recipe hashtags."""

        list_of_hashtags = []
        for recipe_hashtag in recipe_hashtags:
            hashtag_name = recipe_hashtag.hashtags.name
            list_of_hashtags.append(hashtag_name)
        return list_of_hashtags

    @classmethod
    def delete_old_recipe_hashtags(cls, recipeid):
        """Delete the old recipe_hashtags when editing recipe."""

        recipe_hashtags_to_delete = Recipe_Hashtag.query.filter_by(recipe_id=recipeid).delete()

        return recipe_hashtags_to_delete

    @classmethod
    def get_user_recipes_given_hashtag(cls, userid, hashtag):
        """Gets a list of every user recipe with a certain hashtag."""

        QUERY = """
            SELECT recipe_title, recipe_id FROM recipes
            WHERE user_id= :userid AND recipe_id IN
            (SELECT recipe_id FROM recipe_hashtags WHERE hashtag_id IN
            (SELECT hashtag_id FROM hashtags WHERE name= :hashtag))
        """

        cursor = db.session.execute(QUERY, {'userid': userid, 'hashtag': hashtag})
        hashtag_recipes = cursor.fetchall()

        return hashtag_recipes

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Recipe_Hashtag recipe_hashtag_id=%d recipe_id=%d hashtag_id=%d>" % (self.recipe_hashtag_id, self.recipe_id, self.hashtag_id)


############ Hashtag class ############
class Hashtag(db.Model):
    """Where hashtags live."""

    __tablename__ = "hashtags"

    hashtag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    @classmethod
    def get_hashtag_id(cls, hashtag_list):
        """Get hashtag from db or create new db entry."""

        # creates a list of hashtag ids
        # we will use this later to create recipe_hashtag_ids
        hashtag_id_list = []

        for hashtag in hashtag_list:

            #checks if the hashtag already exists in db
            old_hashtag = cls.query.filter_by(name=hashtag).first()

            # if yes, then we get the hashtag_id from the old hashtag
            if old_hashtag is not None:
                hashtag_id = old_hashtag.hashtag_id
                hashtag_id_list.append(hashtag_id)

            # if no, we create a new hashtag, then get the hastag_id from it
            else:
                new_hashtag = Hashtag(name=hashtag)

                db.session.add(new_hashtag)
                db.session.commit()

                hashtag_id = new_hashtag.hashtag_id
                hashtag_id_list.append(hashtag_id)

        return hashtag_id_list

    @classmethod
    def get_readable_hashtags(cls, hashtag_list):
        """Put hashtag names in a traditional format with #."""

        list_of_readable_hashtags = []

        for hashtag in hashtag_list:
            hashtag = '#' + hashtag + " "
            list_of_readable_hashtags.append(hashtag)

        return list_of_readable_hashtags

    @classmethod
    def recreate_hashtag_input(cls, list_of_readable_hashtags):
        """Format the readable hashtags like they would appear in the form input."""

        complete_input = ''

        for hashtag in list_of_readable_hashtags:
            complete_input += hashtag

        return complete_input

    @classmethod
    def get_hashtags_by_user(cls, userid):
        """Get the hashtags for a given user."""

        QUERY = """
        SELECT name FROM hashtags
        WHERE hashtag_id IN (SELECT hashtag_id
        FROM recipe_hashtags
        WHERE recipe_id IN (select recipe_id
        FROM recipes
        WHERE user_id= :userid))
        """

        cursor = db.session.execute(QUERY, {'userid': userid})
        hashtag_data = cursor.fetchall()

        return hashtag_data

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Hashtag hashtag_id=%d name=%s>" % (self.hashtag_id, self.name)


############ Cart_Ingredient class ############
class Cart_Ingredient(db.Model):
    """Associates an ingredient with a user's cart."""

    __tablename__ = "cart_ingredients"

    cart_ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.cart_id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'), nullable=False)

    ingredient = db.relationship("Ingredient")

    @classmethod
    def create_new_cart_ingredient(cls, cartid, ingredientid):
        """Add a cart ingredient to the db."""

        new_cart_ingredient = Cart_Ingredient(cart_id=cartid, ingredient_id=ingredientid)

        db.session.add(new_cart_ingredient)
        db.session.commit()

        return new_cart_ingredient

    @classmethod
    def get_cart_ingredients(cls, cartid):
        """Get ingredients in a cart."""

        cart_ings = Cart_Ingredient.query.filter_by(cart_id=cartid).all()

        return cart_ings

    @classmethod
    def delete_old_cart_ingredients(cls, cartid):
        """Delete old cart ingredients after user has edited cart."""

        deleted_cart_ingredients = Cart_Ingredient.query.filter_by(cart_id=cartid).delete()

        db.session.commit()
        return deleted_cart_ingredients

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Cart_Ingredient cart_ingredient_id=%d cart_id=%d ingredient_id=%d>" % (self.cart_ingredient_id, self.cart_id, self.ingredient_id)


############ Cart class ############
class Cart(db.Model):
    """Cart for a given user."""

    __tablename__ = "carts"

    cart_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    @classmethod
    def create_new_cart(cls, user_id):
        """Add a new cart to the database."""

        new_cart = Cart(user_id=user_id)

        db.session.add(new_cart)
        db.session.commit()

        return new_cart

    @classmethod
    def get_cart_by_id(cls, cart_id):
        """Get a cart from the db given the cart_id."""

        cart = Cart.query.filter_by(cart_id=cart_id).one()

        return cart

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Cart cart_id=%d user_id=%d>" % (self.cart_id, self.user_id)


##############################################################################
# Helper functions

def connect_to_db(app, eatabledata='postgresql://localhost/eatablefaker'):

# def connect_to_db(app, eatabledata='postgresql://localhost/eatabledb'):
    """Connect the database to our Flask app."""

    #Switching the PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = eatabledata
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
