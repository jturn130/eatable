![logo](https://raw.githubusercontent.com/jturn130/eatable/master/static/images/logo.png)

Eatable makes cooking simple by allowing users to store all of their recipes in one place. With Eatable's hashtag feature, users can easily organize, search, and share their recipes without sifting through cookbooks or food blog links. Users can also create a Grocery List from their recipe ingredients, and then have that list texted to them.

## Technology Stack

- PostgreSQL
- SQLAlchemy
- Python
- Flask
- Jinja
- Flask-RESTful
- Javascript
- jQuery
- typeahead.js
- Bootstrap
- Coverage . py
- Flask-Testing
- Twilio API

## Data Model

![data model](https://raw.githubusercontent.com/jturn130/eatable/master/static/images/data_model.jpg)

## How to Use Eatable

Eatable has an intuitive, clean UI

![Homepage](http://g.recordit.co/9wie3PhF4f.gif)

Search your recipes based on a recipe title, ingredient, or hashtag. The typeahead.js plugin will make suggestions for you. Your search triggers an AJAX request, which quickly displays ranked results thanks to PostgreSQL's powerful search features.

![Search feature](http://g.recordit.co/eCmFjl5lyk.gif)

Adding a recipe is simple. Include as many ingredients as you want--the fields just get duplicated with Javascript's `clone()` method.

![Add a recipe](http://g.recordit.co/pp5BndH1m1.gif)

Adding a recipe's ingredients to your cart can be done with a click. The recipe's ingredients are added to an association table in my database, and displayed with Jinja.

![Add to Cart](http://g.recordit.co/HxhuRMiEGd.gif)

## For Developers: The Eatable API

Eatable isn't just for the home chef—businesses can leverage these features with the Eatable API. Thanks to the API, companies can tailor their products and services, as they have their customers' taste preferences at their fingertips.

###### Get a user's ID given their email address
You want: `/api/users/<string:email>`
Returns JSON: `{user.user_id: user.email}`

###### Get a list of user recipes
You want: `/api/recipes/<int:userid>`
Returns JSON: `{recipe_id: recipe_title}`

###### Get a list of user ingredients
You want: `/api/ingredients/<int:userid>`
Returns JSON: `{ingredient_name: count}`

###### Get a list of user hashtags
You want: `/api/hashtags/<int:userid>`
Returns JSON: `{'hashtags': [tags_list]}`

###### Get a list of relevant recipes given a search query
You want: `/api/recipes/search/<string:query>`
Returns JSON: `{recipe id: [recipe title, relevance ranking]}`

## Version 2.0
Coming soon...

Machine learning feature that recommends new recipes around the web, given the recipes a user has already inputted.

## About the Author
Justine Turnbull is an avid chef and software engineer based in San Francisco, CA. You can learn more about her on [LinkedIn](https://www.linkedin.com/in/justineturnbull).