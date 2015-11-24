from model import User, Recipe, Ingredient, Recipe_Hashtag, Hashtag, Cart_Ingredient, Cart, connect_to_db, db
from server import app
import server
import unittest
import doctest
from flask import Flask


def load_tests(loader, tests, ignore):
    """Also run file-based doctests."""

    tests.addTests(doctest.DocFileSuite("tests.txt"))

    return tests


class FlaskTests(unittest.TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Create secret key to access session
        app.secret_key = "ABC"

        # Connect to fake database
        connect_to_db(app, 'postgresql://localhost/eatablefaker')

        app.config['TESTING'] = True

    ################################
    def test_homepage(self):
        """Does the homepage load correctly?"""

        result = self.client.get('/')
        self.assertIn('Take your recipes wherever you go.', result.data)

    def test_signup(self):
        """Does the signup form load correctly?"""

        result = self.client.get('/signup')
        self.assertIn("Just a few short questions", result.data)

    def signup(self, email, password1, phone):
        return self.client.post('/signup-confirm', data={'email': email,
                                'password1': password1, 'phone': phone}, follow_redirects=True)

    def test_signup_confirm(self):
        """Can you sign up for a new account?"""

        result = self.signup('boringbeanies@cool.com', 'coolbeans', '5551234567')

        self.assertIn("You successfully created an account", result.data)
        User.query.filter_by(email='boringbeanies@cool.com').delete()
        db.session.commit()

    def test_signup_confirm_again(self):
        """Does the server recognize if you already have an account?"""

        result = self.signup('turnbull@grinnell.edu', 'coolbeans', '5551234567')

        self.assertIn("You already have an account", result.data)

    def login(self, email, password):
        return self.client.post('/login-confirm', data={'email': email, 'password': password})

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        """Does login/logout work?"""

        result = self.login('test@testing.com', 'jinja2')
        self.assertIn('"confirmed_user": true', result.data)

        result = self.logout()
        self.assertIn('Take your recipes wherever you go.', result.data)

    def test_wrong_login(self):
        """Does password check work?"""

        result = self.login('test@testing.com', '80dqhj')
        self.assertIn('"confirmed_user": false', result.data)

    def recipe_home(self, userid):
        return self.client.get("/myrecipes/%d" % userid)

    def test_recipe_home(self):
        """Does the user homepage display correctly?"""

        self.login('test@testing.com', 'jinja2')
        result = self.recipe_home(14)
        self.assertIn("My Recipes", result.data)

    def search(self, userid, searchQuery):
        return self.client.get("/myrecipes/%d/searchresults?searchQuery=%s" % (userid, searchQuery))

    def test_search(self):
        """Do relevant search results appear?"""

        self.login('jturn130@gmail.com', 'jinja2')
        result = self.search(1, 'vegan')
        self.assertIn("Pineapple Fried Rice", result.data)

    def test_blank_search(self):
        """Do all recipes appear when search is blank?"""

        self.login('jturn130@gmail.com', 'jinja2')
        result = self.search(1, '')
        self.assertIn("Shrimp", result.data)

    def new_recipe_form(self, userid, cartid):
        with self.client.session_transaction() as sess:
            sess['User'] = userid
            sess['Cart'] = cartid
        return self.client.get("/myrecipes/%d/addrecipe" % userid)

    def test_new_recipe_form(self):
        """Does the new recipe form load correctly?"""

        self.login('jturn130@gmail.com', 'jinja2')
        result = self.new_recipe_form(1, 22)
        self.assertIn('Add New Recipe', result.data)

    def typeahead_suggestions(self, userid):
        with self.client.session_transaction() as sess:
            sess['User'] = userid
        return self.client.get("/typeahead")

    def test_typeahead_suggestions(self):
        """Do the typeahead suggestions have the right data?"""

        result = self.typeahead_suggestions(1)
        self.assertIn('vegan', result.data)

    def display_recipe(self, userid, recipeid):
        return self.client.get("/myrecipes/%d/recipe/%d" % (userid, recipeid))

    def test_display_recipe(self):
        """Can an individual recipe be successfully displayed?"""

        result = self.display_recipe(1, 1)
        self.assertIn('Hummus', result.data)

    def edit_recipe_form(self, userid, cartid, recipeid):
        with self.client.session_transaction() as sess:

            sess['User'] = userid
            sess['Cart'] = cartid

        return self.client.get("myrecipes/%d/recipe/%d/edit" % (userid, recipeid))

    def test_edit_recipe_form(self):
        """Does a recipe that's about to edited load in the form fields correctly?"""

        result = self.edit_recipe_form(1, 22, 14)
        self.assertIn('kale', result.data)

    def cart_display(self, userid, cartid):
        with self.client.session_transaction() as sess:

            sess['User'] = userid
            sess['Cart'] = cartid

        return self.client.get("myrecipes/%d/cart/%d" % (userid, cartid))

    def test_cart_display(self):
        """Does the cart page load correctly?"""

        result = self.cart_display(1, 22)
        self.assertIn('My Cart', result.data)

    def edit_cart(self, userid, cartid):
        with self.client.session_transaction() as sess:

            sess['User'] = userid
            sess['Cart'] = cartid

        return self.client.get("myrecipes/%d/cart/%d/editcart" % (userid, cartid))

    def test_edit_cart(self):
        """Does a cart that's about to edited load in the form fields correctly?"""

        result = self.edit_cart(1, 22)
        self.assertIn('Edit Cart', result.data)

    def new_recipe_confirm(self, userid, cartid):
        with self.client.session_transaction() as sess:

            sess['User'] = 14
            sess['Cart'] = cartid

        return self.client.post('/recipe-confirm',
                                data={'qty1': '1', 'measure1': 'cups', 'item1': 'olive oil', 'prepnotes1': 'to taste', 'recipetitle': 'Test Recipe', 'instructions': 'Mix', 'source': 'Moi', 'hashtags': '#easy'},
                                follow_redirects=True)

    def test_new_recipe_confirm(self):
        """Can a new recipe be added to the db?"""

        result = self.new_recipe_confirm(14, 209)
        self.assertIn('Hooray!', result.data)

    def bad_recipe_confirm(self, userid, cartid):
        with self.client.session_transaction() as sess:

            sess['User'] = 14
            sess['Cart'] = cartid

        return self.client.post('/recipe-confirm',
                                data={'qty1': 1, 'measure1': 'cups', 'item1': 'olive oil', 'prepnotes1': 'to taste', 'instructions': 'Mix', 'source': 'Moi', 'hashtags': '#easy'},
                                follow_redirects=True)

    def test_bad_recipe_confirm(self):
        """Does a bad attempt at adding a recipe redirect to the homepage?"""

        result = self.bad_recipe_confirm(14, 209)
        self.assertIn('Take your recipes', result.data)

    def recipe_edit_confirm(self, userid, cartid, recipeid):
        with self.client.session_transaction() as sess:

            sess['User'] = userid
            sess['Cart'] = cartid

        return self.client.post('/myrecipes/%d/recipe/%d/edit-confirm' % (userid, recipeid),
                                data={'qty1': '1', 'measure1': 'cups', 'item1': 'olive oil', 'prepnotes1': 'to taste', 'recipetitle': 'Test Recipe', 'instructions': 'Mix', 'source': 'Moi', 'hashtags': '#easy'},
                                follow_redirects=True)

    def test_recipe_edit_confirm(self):
        """Can an edited recipe be updated in the db?"""

        result = self.recipe_edit_confirm(14, 209, 74)
        self.assertIn('You have successfully edited your recipe', result.data)

    def add_a_recipe_to_cart(self, recipeid, userid, cartid):
        Cart_Ingredient.query.filter_by(cart_id=cartid).delete()

        with self.client.session_transaction() as sess:

            sess['User'] = userid
            sess['Cart'] = cartid

        return self.client.get('/myrecipes/%d/recipe/%d/addtocart' % (userid, recipeid), follow_redirects=True)

    def test_add_a_recipe_to_cart(self):
        """Can you add a recipe's ingredients to your grocery cart?"""

        result = self.add_a_recipe_to_cart(68, 14, 209)
        self.assertIn('added your recipe to your grocery cart.', result.data)

    def edited_cart_update(self, userid, cartid):
            with self.client.session_transaction() as sess:

                sess['User'] = userid
                sess['Cart'] = cartid

            return self.client.post('/myrecipes/%d/cart/%d/edit-confirm' % (userid, cartid),
                                    data={'qty1': '1', 'item1': 'olive oil', 'item2': 'salt', 'item3': 'pepper', 'item4': 'eggplant', 'item5': 'tomatoes', 'item6': 'carrots', 'item7': 'onions', 'item8': 'lentils', 'item9': 'fava beans', 'item10': 'lima beans'},
                                    follow_redirects=True)

    def test_edited_cart_update(self):
        """Can a user successfully edit their grocery cart?"""

        result = self.edited_cart_update(14, 209)
        self.assertIn('My Cart', result.data)

    def cart_delete(self, userid, cartid):
        with self.client.session_transaction() as sess:

            sess['User'] = userid

        return self.client.get('/myrecipes/%d/cart/%d/deletecart' % (userid, cartid), follow_redirects=True)

    def test_cart_delete(self):
        """Can a user successfully create a new cart?"""

        result = self.cart_delete(14, 209)
        self.assertIn('Parting is such sweet sorrow', result.data)

    def twilio(self, userid, cartid):
        with self.client.session_transaction() as sess:

            sess['User'] = userid
            sess['Cart'] = cartid

        return self.client.get('/sms', follow_redirects=True)

    def test_twilio(self):
        """Will the user get redirected after their SMS is sent?"""

        result = self.twilio(1, 22)
        self.assertIn('My Recipes', result.data)


################################################################################

if __name__ == '__main__':
    unittest.main()
