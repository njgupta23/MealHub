import os
import unirest
import ast
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Recipe, UserRecipe, SearchNutriData


app = Flask(__name__)
app.secret_key = "secret..."

#SPOONACULAR_KEY = os.environ['SPOONACULAR_KEY']

@app.route('/')
def index():
    """Homepage."""

    # if session != {}:
    #     user = User.query.get(session["user_id"])

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
    """Process search form and display results. Temporarily store results in db."""

    user = User.query.get(session["user_id"])

########## UNCOMMENT THIS SECTION FOR ACTUAL API REQUESTS ##########

    # request.args is a multidict, so need to use .getlist (not .get)
    cuisines = request.args.getlist("cuisine")
    exclude = request.args.get("exclude")
    intolerant = request.args.getlist("intolerant")

    # make intolerant list into comma-separated string
    intolerant_str = ""
    for word in intolerant:
        intolerant_str += word + ","

    headers = {
                "X-Mashape-Key": "nAiQmpcpwZmsh6s601aNDvJCwVZjp1EzxBdjsnZZ0a0c585kU0",
                "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com",
                "Accept": "application/json"
                }

    params_search = {
                       "number": 12 / len(cuisines),    # to accomodate for 1-3 cuisine inputs
                       "offset": 0,
                       "query": "main course",
                       "limitLicense": False,
                       "instructionsRequired": True,
                       "type": "main course",
                       "diet": "vegetarian",
                       "intolerances": intolerant_str,
                       "excludeIngredients": exclude,
                       "cuisine": cuisines
                    }

    domain_url = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com"
    search_url = "{}/recipes/search?".format(domain_url)
    results = []    # a list of dicts

    for cuisine in cuisines:
        params_search["cuisine"] = cuisine

        response = unirest.get(search_url,
                               headers=headers,
                               params=params_search
                               )
        results.extend(response.body["results"])

    params_nutrition = {"includeNutrition": True}
    for result in results:
        recipe_id = result["id"]    # need this for second GET request (for nutrient info)
        nutrition_url = "{}/recipes/{}/information?".format(
                domain_url,
                recipe_id
            )
        nutrition = unirest.get(
            nutrition_url,
            headers=headers,
            params=params_nutrition
        )
        nutrition_results = nutrition.body["nutrition"]['nutrients']
        result["nutrition"] = nutrition_results    # nutrition_results is a list of dicts
        result["url"] = nutrition.body["sourceUrl"]
        result["image"] = nutrition.body["image"]

    ## store search results in SearchNutriData table (to access info for charts)

    # clear SearchNutriData table to start fresh
    db.session.query(SearchNutriData).delete()

    # add new search results nutri data to table
    for result in results:
        nutridata = SearchNutriData(fat=result["nutrition"][1]["percentOfDailyNeeds"],
                                    carbohydrates=result["nutrition"][3]["percentOfDailyNeeds"],
                                    protein=result["nutrition"][7]["percentOfDailyNeeds"]
                                    )
        db.session.add(nutridata)

    db.session.commit()




    ####### MOCK RESULTS DICT FOR TESTING #########

    # mock_results = [{
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }, {
    #     "id": 479101,
    #     "url": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
    #     "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
    #     "title": "On the Job: Pan Roasted Cauliflower From Food52",
    #     "readyInMinutes": 20,
    #     "nutrition": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]
    # }
    # ]


    return render_template("results.html", results=results, fname=user.fname)


@app.route("/save-recipes", methods=['POST'])
def save_recipe():
    """Stores a saved recipe into database."""
    user = User.query.get(session["user_id"])

    recipes = []
    user.saved_recipes = []
    for i in range(1, 6):
        recipes.append(ast.literal_eval(request.form.get("recipe-{}".format(i))))
        recipe = db.session.query(Recipe).filter_by(recipe_id=recipes[i-1]["id"]).first()
        if recipe is not None:
            recipe.num_saved += 1
        else:
            recipe = Recipe(recipe_id=recipes[i-1]["id"],
                            title=recipes[i-1]["title"],
                            url=recipes[i-1]["url"],
                            image=recipes[i-1]["image"],
                            prep_time=recipes[i-1]["prepTime"],
                            num_saved=1,
                            fat=recipes[i-1]["fat"],
                            carbohydrates=recipes[i-1]["carbs"],
                            protein=recipes[i-1]["protein"])
            db.session.add(recipe)

        user.saved_recipes.append(recipe)

    db.session.commit()

    return redirect("/mymeals")


@app.route("/mymeals")
def show_saved_recipes():
    """Displays saved recipes."""

    user = User.query.get(session["user_id"])
    recipes = user.saved_recipes     # a list of 5 saved recipes

    return render_template("my_meals.html", recipes=recipes, fname=user.fname)


@app.route("/fat-data-list.json")
def fat_data():
    """Return percentDailyNeeds of fat for a recipe."""

    # need a for loop to loop through the 12 results?? then make 12 fat_dicts??

    fat_data = db.session.query(SearchNutriData.fat).all()
    fat_data_list = []    # a list of fat dicts

    for fat in fat_data:

        fat_dict = {
                    "labels": [
                        "Fat",
                        "Remainder",
                    ],
                    "datasets": [
                        {
                            "data": [fat, 100-fat],
                            "backgroundColor": [
                                "#FF6384",
                                "gray"
                            ],
                            "hoverBackgroundColor": [
                                "#FF6384",
                                "gray"
                            ]
                        }]
                }

        fat_data_list.append(fat_dict)

    return jsonify(fat_data_list)    # can I jsonify a list or just a dict?


@app.route("/carbs-data.json")
def carbs_data():
    """Return percentDailyNeeds of carbs for a recipe."""

    carbs_dict = {
                "labels": [
                    "Carbohydrates",
                    "Remainder",
                ],
                "datasets": [
                    {
                        "data": [50, 50],
                        "backgroundColor": [
                            "blue",
                            "gray"
                        ],
                        "hoverBackgroundColor": [
                            "blue",
                            "gray"
                        ]
                    }]
            }

    return jsonify(carbs_dict)


@app.route("/protein-data.json")
def protein_data():
    """Return percentDailyNeeds of protein for a recipe."""

    protein_dict = {
                "labels": [
                    "Protein",
                    "Remainder",
                ],
                "datasets": [
                    {
                        "data": [25, 75],
                        "backgroundColor": [
                            "green",
                            "gray"
                        ],
                        "hoverBackgroundColor": [
                            "green",
                            "gray"
                        ]
                    }]
            }

    return jsonify(protein_dict)


@app.route('/chart')
def show_chart():

    return render_template("chart.html")

######### Helper functions ##########

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    connect_to_db(app)
    app.run("0.0.0.0", debug=True)
