![logo](https://raw.githubusercontent.com/jturn130/eatable/master/static/images/logo.png)

Eatable makes cooking simple by allowing users to store all of their recipes in one place. With Eatable's hashtag feature, users can easily organize, search, and share their recipes without sifting through cookbooks or food blog links. Users can also create a Grocery List from their recipe ingredients, and have that list texted to them.

## About the Author
Justine Turnbull is an avid chef and software engineer based in San Francisco, CA. She loves full-stack web development and burritos equally. You can learn more about her on [LinkedIn](https://www.linkedin.com/in/justineturnbull), as she is actively seeking employment.

## Technology Stack

- [Python](https://www.python.org/)
- [PostgreSQL](http://www.postgresql.org/)
- [SQLAlchemy](http://www.sqlalchemy.org/)
- [Flask, a Python web framework](http://flask.pocoo.org/)
- [Jinja](http://jinja.pocoo.org/docs/dev/)
- [Javascript](https://www.javascript.com/)
- [jQuery](https://jquery.com/)
- [Flask-RESTful](https://flask-restful-cn.readthedocs.org/en/0.3.4/)
- [Bootstrap](http://getbootstrap.com/)
- [Python Test Coverage](https://pypi.python.org/pypi/coverage)
- [Flask-Testing](https://pythonhosted.org/Flask-Testing/)
- [typeahead.js](https://twitter.github.io/typeahead.js/)

## How to Use Eatable

###### Eatable has an intuitive, clean UI

![Homepage](http://g.recordit.co/9wie3PhF4f.gif)  
<br><br>
###### Search your recipes based on a recipe title, ingredient, or hashtag. The typeahead.js plugin will make suggestions for you. Your search triggers an AJAX request, which quickly displays ranked results thanks to PostgreSQL's powerful search features.

![Search feature](http://g.recordit.co/eCmFjl5lyk.gif)  
<br><br>
###### Adding a recipe is simple. Include as many ingredients as you want--the fields just get duplicated with Javascript's `clone()` method.

![Add a recipe](http://g.recordit.co/pp5BndH1m1.gif)  
<br><br>
###### Adding a recipe's ingredients to your cart can be done with a click. The recipe's ingredients are added to an association table in the database, and displayed with Jinja.

![Add to Cart](http://g.recordit.co/HxhuRMiEGd.gif)
<br><br>
###### Eatable can send a text with your grocery list via the Twilio API (with a Python wrapper).

![Cart SMS](https://raw.githubusercontent.com/jturn130/eatable/master/static/images/iphone.jpg)  

## For Developers: The Eatable API

Eatable isn't just for the home chef—businesses can leverage these features with the RESTful Eatable API. Thanks to the API, companies can tailor their products and services, as they have their customers' taste preferences at their fingertips.  

<br><br>
![API](http://g.recordit.co/XkqFzyDjar.gif)
<br><br>

### API Tips & Tricks  

###### Get a user's ID given their email address
You want: `/api/users/<string:email>`  

Returns JSON: `{user_id: user_email}`  

Example: `{"14": "test@testing.com"}`

###### Get a list of user recipes
You want: `/api/recipes/<int:userid>`  

Returns JSON: `{recipe_id: recipe_title}`  

Example: `{"15": "Stewy Shrimp with Tomatoes and White Beans", "16": "Ratatouille", "30": "Avocado Bean Salad", "31": "Cajun Collard Greens"}`

###### Get a list of user ingredients
You want: `/api/ingredients/<int:userid>`  

Returns JSON: `{ingredient_name: count}`  

Example: `{"olive oil": 7, "love": 1, "cucumber": 1, "cereal": 1, "arugula": 1, "lemon juice": 1, "green pepper": 1, "oregano": 2, "green onions": 2, "dijon mustard": 1, "brown rice": 1, "large shrimp": 1, "parsley": 1, "red pepper": 1, "chickpeas": 2, "red pepper flakes": 1, "salt": 6, "diced tomatoes": 4}`

###### Get a list of user hashtags
You want: `/api/hashtags/<int:userid>`  

Returns JSON: `{'hashtags': [tags_list]}`

Example: `{"hashtags": ["myown", "vegan", "vegetarian", "chinese", "mom", "kale", "lunch", "shrimp", "seafood", "healthy", "cool", "stew", "meat", "comfortfood", "dessert", "chocolate", "soup", "delicious"]}`

###### Get a list of relevant recipes given a search query\s\s
You want: `/api/recipes/search/<string:query>`  

Returns JSON: `{recipe id: [recipe title, relevance ranking]}`  

Example: `{"1": ["Hummus", 0.198206], "34": ["French Onion Soup", 0.198206], "10": ["Couscous Salad", 0.198206], "15": ["Stewy Shrimp with Tomatoes and White Beans", 0.198206], "16": ["Ratatouille", 0.198206], "30": ["Avocado Bean Salad", 0.198206], "31": ["Cajun Collard Greens", 0.198206]}`

## Version 2.0
Coming soon...

Machine learning feature that recommends new recipes around the web, given the recipes a user has already inputted.


## How to Run the Eatable Flask App Locally

  * Git clone this repo
  * Set up and activate a python virtualenv, and install all dependencies:
    * `pip install -r requirements.txt`
  * Make sure you have PostgreSQL running. Create a new database in psql named *eatabledb*:
    * `psql`
    * `CREATE DATABASE eatabledb;`
  * Create the tables in your database:
    * `python -i model.py`
    * While in interactive mode, create tables: `db.create_all()`
  * Now, quit interactive mode. Start up the flask server:
    * `python server.py`
  * Go to localhost:5000 to see the web app

## Data Model

![data model](https://raw.githubusercontent.com/jturn130/eatable/master/static/images/data_model.png)  