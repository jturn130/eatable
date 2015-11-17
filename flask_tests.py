from model import User, Recipe, Ingredient, Recipe_Hashtag, Hashtag, Cart_Ingredient, Cart, connect_to_db, db
from server import app
import server
import unittest


class FlaskTests(unittest.TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Connect to fake database
        connect_to_db(app, 'postgresql://localhost/eatablefaker')

    def test_homepage(self):
        """Does homepage load correctly?"""

        result = self.client.get('/')
        self.assertIn('Take your recipes wherever you go.', result.data)

    def test_signup(self):
        """Does signup form load correctly?"""

        result = self.client.get('/signup')
        self.assertIn("Just a few short questions", result.data)

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


################################################################################

if __name__ == '__main__':
    unittest.main()
