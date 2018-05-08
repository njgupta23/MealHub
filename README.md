# MealHub

MealHub is a web app designed to help with vegetarian meal planning. Users search for recipes based on food preferences. A nutrient tracker allows users to plan meals according to recommended daily allowances of major macronutrients.  Integration with Google Calendar allows users to send recipes to their personal calendar.

### Features
![MealHub Homepage](https://github.com/njgupta23/MealHub/blob/master/static/MealHub%20Homepage.png)

Create an account or sign in to create and access meal plans.

![MealHub Create Account](https://github.com/njgupta23/MealHub/blob/master/static/MealHub%20Create%20Account.png)

Search for recipes based on cuisine preferences, foods to avoid, and dietary restrictions.

![MealHub New Plan](https://github.com/njgupta23/MealHub/blob/master/static/MealHub%20New%20Plan.png)

Select recipes for a meal plan based on prep time and recommended daily allowances of major macronutrients. View weekly totals of macronutrients based on selected recipes.

![MealHub Results](https://github.com/njgupta23/MealHub/blob/master/static/MealHub%20Results.png)

Save meal plans and add recipes to Google calendar for easy access.

![MealHub My Meals](https://github.com/njgupta23/MealHub/blob/master/static/MealHub%20My%20Meals.png)


### Tech

Backend: Python, Flask, PostgreSQL, SQLAlchemy

Frontend: JavaScript, Chart.js, jQuery, AJAX, Jinja, Bootstrap, HTML5, CSS

APIs: Spoonacular, Google Calendar

### Installation

MealHub requires [Python 2.7](https://www.python.org/downloads/release/python-2714/) and [PostgreSQL](https://www.postgresql.org/) to run.

Clone this repository.

```sh
$ git clone https://github.com/njgupta23/MealHub.git
```

Create and activate a virtual environment inside your MealHub directory.

```sh
$ virtualenv env
$ source env/bin/activate
```

Install the dependencies.

```sh
$ pip install -r requirements.txt
```

Get keys to the [Spoonacular](https://spoonacular.com/food-api) and [Google Calendar](https://developers.google.com/calendar/) APIs.

Store them in a secrets.sh file, similar to this:

```sh
export SPOONACULAR_KEY='abc'
export GOOGLE_CLIENT_ID='abc'
export GOOGLE_CLIENT_SECRET='abc'
```

Create your database.

```sh
$ createdb mealhub
$ python model.py
```

Run the server.

```sh
$ python server.py
```

### For Version 2.0

- Implement in React
- Make changes to current and past meal plans
- Select meal plan dates that have not already been used

### About the Developer

MealHub was created by Neha Gupta, a doctor turned developer in the Bay Area, CA. Learn more about the developer on [LinkedIn](https://www.linkedin.com/in/nehajgupta/).
