import os
import unirest
import ast
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Recipe, UserRecipe


app = Flask(__name__)
app.secret_key = "secret..."

#SPOONACULAR_KEY = os.environ['SPOONACULAR_KEY']

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


# route after new account form submitted (modal) or after logging in
@app.route('/profile', methods=['POST'])
def new_user_profile():
    """Process login or account creation and display user profile page."""

    # Get form vars
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    bday = request.form["bday"]
    gender = request.form["gender"]
    pw = request.form["pw"]

    new_user = User(fname=fname, lname=lname, email=email, pw=pw, bday=bday, gender=gender)

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.user_id

    return render_template("user_profile.html", fname=fname)


@app.route('/signin', methods=['GET'])
def signin_form():
    """Display sign in form."""

    return render_template("signin_form.html")


@app.route('/signin', methods=['POST'])
def signin_process():
    """Process sign in form."""

    #Get form vars
    email = request.form["email"]
    pw = request.form["pw"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/signin")

    if user.pw != pw:
        flash("Incorrect password")
        return redirect("/signin")

    session["user_id"] = user.user_id

    return redirect("/profile-{}".format(user.user_id))


@app.route('/profile-<int:user_id>')
def user_profile(user_id):
    """Display user profile page."""

    user = User.query.get(user_id)
    return render_template("user_profile.html", fname=user.fname)


@app.route('/signout')
def signout():
    """Log out."""

    del session["user_id"]
    return redirect("/")


@app.route('/results', methods=['GET'])
def process_search():
    """Process search form and display results."""

########## UNCOMMENT THIS SECTION FOR ACTUAL API REQUESTS ##########

    # # request.args is a multidict, so need to use .getlist (not .get)
    # cuisines = request.args.getlist("cuisine")
    # exclude = request.args.get("exclude")
    # intolerant = request.args.getlist("intolerant")

    # # make intolerant list into comma-separated string
    # intolerant_str = ""
    # for word in intolerant:
    #     intolerant_str += word + ","

    # headers = {
    #             "X-Mashape-Key": "nAiQmpcpwZmsh6s601aNDvJCwVZjp1EzxBdjsnZZ0a0c585kU0",
    #             "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com",
    #             "Accept": "application/json"
    #             }

    # params_search = {
    #                    "number": 12 / len(cuisines),    # to accomodate for 1-3 cuisine inputs
    #                    "offset": 0,
    #                    "query": "main course",
    #                    "limitLicense": False,
    #                    "instructionsRequired": True,
    #                    "type": "main course",
    #                    "diet": "vegetarian",
    #                    "intolerances": intolerant_str,
    #                    "excludeIngredients": exclude,
    #                    "cuisine": cuisines
    #                 }

    # domain_url = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com"
    # search_url = "{}/recipes/search?".format(domain_url)
    # results = []

    # for cuisine in cuisines:
    #     params_search["cuisine"] = cuisine

    #     response = unirest.get(search_url,
    #                            headers=headers,
    #                            params=params_search
    #                            )
    #     results.extend(response.body["results"])


    # params_nutrition = {"includeNutrition": True}
    # for result in results:
    #     recipe_id = result["id"]    # need this for second GET request (for nutrient info)
    #     nutrition_url = "{}/recipes/{}/information?".format(
    #             domain_url,
    #             recipe_id
    #         )
    #     nutrition = unirest.get(
    #         nutrition_url,
    #         headers=headers,
    #         params=params_nutrition
    #     )
    #     nutrition_results = nutrition.body["nutrition"]['nutrients']
    #     result["nutrition"] = nutrition_results    # nutrition_results is a list of dicts
    #     result["url"] = nutrition.body["sourceUrl"]
    #     result["image"] = nutrition.body["image"]

    nutrients = [1,3,7]

    ####### MOCK RESULTS DICT FOR TESTING #########

    mock_results = [{
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }, {
        "id": 479101,
        "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
        "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
        "title": "On the Job: Pan Roasted Cauliflower From Food52",
        "readyInMinutes": 20,
        "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    }
    ]

    return render_template("results.html", results=mock_results, nutrients=nutrients)

@app.route("/save-recipe", methods=['POST'])
def save_recipe():
    """Stores a saved recipe into database."""
    # recipe = ast.literal_eval(request.form.get("recipe-1"))
    # print recipe
    # print type(recipe)

    recipes = []    # a list of dicts with data from the 5 saved recipes
    for i in range(1, 6):
        recipes.append(ast.literal_eval(request.form.get("recipe-{}".format(i))))
        # check if recipe is in db
        # if yes: update num_saved to num_saved+1
        # if no: add to db and num_saved=1
        recipe = db.session.query(Recipe).filter_by(recipe_id=recipes[i-1]["id"]).first()
        if recipe is not None:
            recipe.num_saved += 1
            db.session.commit()
        else:
            recipe = Recipe(recipe_id=recipes[i-1]["id"],
                            title=recipes[i-1]["title"],
                            url=recipes[i-1]["url"],
                            image=recipes[i-1]["image"],
                            prep_time=recipes[i-1]["prepTime"],
                            num_saved=1)
            db.session.add(recipe)
            db.session.commit()
    return render_template("my_meals.html")


# @app.route("/my-meals")

######### Helper functions ##########

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    connect_to_db(app)
    app.run("0.0.0.0", debug=True)
