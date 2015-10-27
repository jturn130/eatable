"""Models and database functions for Eatable."""

from flask_sqlalchemy import SQLAlchemy

# Connection to the SQLite database via the Flask-SQLAlchemy helper library
# On this, we can find the `session` object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of Eatable."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    mobile_phone = db.Column(db.String(30), nullable=True)

    @classmethod
    def get_user_by_email(cls, user_email):

        try:
            user_login_info = cls.query.filter_by(email=user_email).one()
            return user_login_info

        except Exception, error:
            print error

    @classmethod
    def create_new_user(cls, user_email, user_password, user_phone):

        user = User(email=user_email, password=user_password, mobile_phone=user_phone)

        ### confirm with staff this is the right place to add/commit
        ### can or should I do this in the server file?
        db.session.add(user)
        db.session.commit()

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%d email=%s>" % (self.user_id, self.email)


class Recipe(db.Model):
    """Eatable recipe for a given user."""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipe_title = db.Column(db.String(150), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Recipe recipe_id=%d user_id=%d recipe_title=%s>" % (self.recipe_id, self.user_id, self.recipe_title)


class Ingredient(db.Model):
    """Individual ingredient information for a given recipe."""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    quantity = db.Column(db.String(10), nullable=True)
    measure = db.Column(db.String(50), nullable=True)
    item = db.Column(db.String(75), nullable=False)
    prep_notes = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Ingredient ingredient_id=%d recipe_id=%d item=%s>" % (self.ingredient_id, self.recipe_id, self.item)


class Recipe_Hashtag(db.Model):
    """Associates a hashtag with a specific recipe."""

    __tablename__ = "recipe_hashtags"

    recipe_hashtag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtags.hashtag_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Recipe_Hashtag recipe_hashtag_id=%d recipe_id=%d hashtag_id=%d>" % (self.recipe_hashtag_id, self.recipe_id, self.hashtag_id)


class Hashtag(db.Model):
    """Where hashtags live."""

    __tablename__ = "hashtags"

    hashtag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Hashtag hashtag_id=%d name=%s>" % (self.hashtag_id, self.name)


class Cart_Ingredient(db.Model):
    """Associates an ingredient with a user's cart."""

    __tablename__ = "cart_ingredients"

    cart_ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.cart_id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Cart_Ingredient cart_ingredient_id=%d cart_id=%d ingredient_id=%d>" % (self.cart_ingredient_id, self.cart_id, self.ingredient_id)


class Cart(db.Model):
    """Cart for a given user."""

    cart_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Cart cart_id=%d user_id=%d>" % (self.cart_ingredient_id, self.cart_id, self.user_id)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eatable.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
