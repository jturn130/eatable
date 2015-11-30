![logo](https://raw.githubusercontent.com/jturn130/eatable/master/static/images/logo.png)

Eatable makes cooking simple by allowing users to store all of their recipes in one place. With Eatable's hashtag feature, users can easily organize, search, and share their recipes without sifting through cookbooks or food blog links. Users can also create a Grocery List from their recipe ingredients, and have that list texted to them.

## About the Author
Justine Turnbull is an avid chef and software engineer based in San Francisco, CA. She loves full-stack web development and burritos equally. You can learn more about her on [LinkedIn](https://www.linkedin.com/in/justineturnbull), as she is actively seeking employment.

## Technology Stack

- Python
- PostgreSQL
- SQLAlchemy
- Flask, a Python web framework
- Jinja
- Javascript
- jQuery
- Flask-RESTful
- Bootstrap
- Python Test Coverage
- Flask-Testing
- typeahead.js

## How to Use Eatable

###### Eatable has an intuitive, clean UI

![Homepage](http://g.recordit.co/9wie3PhF4f.gif)  
***   
<br>
###### Search your recipes based on a recipe title, ingredient, or hashtag. The typeahead.js plugin will make suggestions for you. Your search triggers an AJAX request, which quickly displays ranked results thanks to PostgreSQL's powerful search features.

![Search feature](http://g.recordit.co/eCmFjl5lyk.gif)  
*** 
<br>
###### Adding a recipe is simple. Include as many ingredients as you want--the fields just get duplicated with Javascript's `clone()` method.

![Add a recipe](http://g.recordit.co/pp5BndH1m1.gif)  
*** 
<br>
###### Adding a recipe's ingredients to your cart can be done with a click. The recipe's ingredients are added to an association table in the database, and displayed with Jinja.

![Add to Cart](http://g.recordit.co/HxhuRMiEGd.gif)
***
<br>
###### Eatable can send a text with your grocery list via the Twilio API.

![Cart SMS](https://raw.githubusercontent.com/jturn130/eatable/master/static/images/iphone.jpg)  

## For Developers: The Eatable API

Eatable isn't just for the home chef—businesses can leverage these features with the RESTful Eatable API. Thanks to the API, companies can tailor their products and services, as they have their customers' taste preferences at their fingertips.

###### Get a user's ID given their email address
You want: `/api/users/<string:email>`  

Returns JSON: `{user_id: user.email}`

###### Get a list of user recipes
You want: `/api/recipes/<int:userid>`  

Returns JSON: `{recipe_id: recipe_title}`

###### Get a list of user ingredients
You want: `/api/ingredients/<int:userid>`  

Returns JSON: `{ingredient_name: count}`

###### Get a list of user hashtags
You want: `/api/hashtags/<int:userid>`  

Returns JSON: `{'hashtags': [tags_list]}`

###### Get a list of relevant recipes given a search query\s\s
You want: `/api/recipes/search/<string:query>`  

Returns JSON: `{recipe id: [recipe title, relevance ranking]}`

## Version 2.0
Coming soon...

Machine learning feature that recommends new recipes around the web, given the recipes a user has already inputted.


## How to Run the Eatable Flask App Locally

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