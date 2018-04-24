import os
import unirest
import ast
import random
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Recipe, Plan, PlanRecipe
from sqlalchemy import desc

import flask
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
#SPOONACULAR_KEY = os.environ['SPOONACULAR_KEY']

app = Flask(__name__)
app.secret_key = "secret..."

headers = {
            "X-Mashape-Key": "nAiQmpcpwZmsh6s601aNDvJCwVZjp1EzxBdjsnZZ0a0c585kU0",
            "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com",
            "Accept": "application/json"
            }

domain_url = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com"


########################### Google API ############################


@app.route('/test')
def test_api_request():
    """Checks if user authorization has been received.
    Makes a Google Calendar API request to create an event."""

    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    calendar = build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    plan = Plan.query.filter_by(plan_id=session["plan_id"]).first()
    recipes = plan.recipes
    d = plan.start
    date = "{}-{}-{}".format(d.year, d.month, d.day)
    # 5 events that will be added to calendar
    for recipe in recipes:
        event = {
                'summary': recipe.title,
                'description': recipe.url,
                'start': {
                    'date': date,   # need to increment dates and add time
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'date': date,
                    'timeZone': 'America/Los_Angeles',
                },
                }

        event = calendar.events().insert(calendarId='primary', body=event).execute()

    # flash('Event created: {}'.format(event.get('htmlLink')))

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(credentials)

    # return jsonify(**event)
    return redirect("/mymeals-{}".format(plan.plan_id))


@app.route('/authorize')
def authorize():
    """Requests user's permission to submit API requests on behalf of user."""

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    """Continuation of OAuth authorization proccess."""
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(flask.url_for('test_api_request'))


# @app.route('/revoke')
# def revoke():
#     if 'credentials' not in session:
#         return ('You need to <a href="/authorize">authorize</a> before ' +
#             'testing the code to revoke credentials.')

#     credentials = google.oauth2.credentials.Credentials(
#         **session['credentials'])

#     revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
#         params={'token': credentials.token},
#         headers = {'content-type': 'application/x-www-form-urlencoded'})

#     status_code = getattr(revoke, 'status_code')
#     if status_code == 200:
#         return('Credentials successfully revoked.')
#     else:
#         return('An error occurred.')


@app.route('/clear')
def clear_credentials():
    """Clears authorization credentials that are stored in the Flask session."""

    if 'credentials' in session:
        del session['credentials']
    return redirect("/")



def credentials_to_dict(credentials):
    """Returns a dictionary of user credentials."""

    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

###################################################################


@app.route('/')
def index():
    """Homepage."""

    # if session != {}:
    #     user = User.query.get(session["user_id"])

    return render_template("homepage.html")


# route after new account form submitted (modal) or after logging in
@app.route('/new-account', methods=['POST'])
def new_user_profile():
    """Process account creation and display my meals page."""

    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    bday = request.form["bday"]
    gender = request.form["gender"]
    pw = request.form["pw"]

    if User.query.filter_by(email=email).first() is None:
        new_user = User(fname=fname, lname=lname, email=email, pw=pw, bday=bday, gender=gender)
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.user_id
        return redirect("/mymeals")
    # need to check that same email doesn't exist... need stay in same modal
    # else:
    #     flash("That email is already registered. Try another.")
    #     return redirect("/")


@app.route('/signin', methods=['GET'])
def signin_form():
    """Display sign in form."""

    return render_template("signin_form.html")


@app.route('/signin', methods=['POST'])
def signin_process():
    """Process sign in form."""

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

    return redirect("/mymeals")


@app.route('/profile-<int:user_id>')
def user_profile(user_id):
    """Display user profile page."""

    user = User.query.get(user_id)
    return render_template("user_profile.html", fname=user.fname)


@app.route('/signout')
def signout():
    """Log out."""

    del session["user_id"]
    return redirect("/clear")


@app.route('/results', methods=['POST'])
def process_search():
    """Process search form and display results."""

    user = User.query.get(session["user_id"])
    # get the plan start date from the form
    start = request.form.get("start")
    # make a new record in the plan table
    plan = Plan(start=start,
                user_id=user.user_id,
                )
    db.session.add(plan)
    db.session.commit()
    # store the plan_id in flask session
    session["plan_id"] = plan.plan_id

########## UNCOMMENT THIS SECTION FOR ACTUAL API REQUESTS ##########

    # request.args is a multidict, so need to use .getlist (not .get)
    cuisines = request.form.getlist("cuisine")
    exclude = request.form.get("exclude")
    intolerant = request.form.getlist("intolerant")

    # make intolerant list into comma-separated string
    intolerant_str = ""
    for word in intolerant:
        intolerant_str += word + ","

    number = 12 / len(cuisines)    # to accomodate for 1-3 cuisine inputs
    results = []    # a list of dicts

    while len(results) < 12:
        for cuisine in cuisines:
            # params_search["cuisine"] = cuisine
            response = make_recipe_search_request(number, cuisine, exclude, intolerant_str)
            results.extend(response.body["results"])

    ids = ""
    for result in results:
        recipe_id = str(result["id"])
        ids += recipe_id + ","

    nutrition = make_nutrition_info_request(ids)

    for i in range(len(results)):    # nutrition.body is a list of info for each result
        results[i]["nutrition"] = nutrition.body[i]["nutrition"]["nutrients"]    # this is a list of dicts
        results[i]["url"] = nutrition.body[i]["sourceUrl"]
        results[i]["image"] = nutrition.body[i]["image"]

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

    plan = Plan.query.get(session["plan_id"])

    recipes = []
    plan.recipes = []
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

        plan.recipes.append(recipe)

    db.session.commit()

    # remove plan_id from flask session
    # del session["plan_id"]

    return redirect("/mymeals")


@app.route("/mymeals")
def check_for_plans():
    """Checks if user has any saved meal plans."""

    user = User.query.get(session["user_id"])

    if (Plan.query.filter_by(user_id=user.user_id).first()) is not None:
        # order by plan_id and get highest number
        plan = Plan.query.filter_by(user_id=user.user_id).order_by(desc(Plan.plan_id)).first()
        return redirect("/mymeals-{}".format(plan.plan_id))
    else:
        return render_template("no_meals.html", fname=user.fname)


@app.route("/mymeals-<int:plan_id>")
def show_saved_recipes(plan_id):
    """Displays a meal plan."""

    session["plan_id"] = plan_id    # do i need this?

    user = User.query.get(session["user_id"])
    plan = Plan.query.filter_by(plan_id=plan_id).first()
    recipes = plan.recipes
    # all past plans made by current user
    past_plans = Plan.query.filter_by(user_id=user.user_id).all()

    return render_template("my_meals.html", plan=plan, recipes=recipes, fname=user.fname, past_plans=past_plans)


@app.route("/fat-data.json")
def fat_data():
    """Return percentage of fat for the five saved recipes."""

    user = User.query.get(session["user_id"])
    # plan = Plan.query.filter_by(user_id=user.user_id).order_by(desc(Plan.plan_id)).first()
    plan = Plan.query.get(session["plan_id"])
    recipes = plan.recipes

    color = "#4A7E13"
    fat = 0

    for recipe in recipes:
        fat += recipe.fat

    fat = (fat*3)/5

    if fat > 100:
        fat = 100
        color = "#E04732"

    fat_dict = {
                "labels": [
                    "Fat",
                    "Remainder",
                ],
                "datasets": [
                    {
                        "data": [fat, 100-fat],
                        "backgroundColor": [
                            color,
                            "gray"
                        ],
                        "hoverBackgroundColor": [
                            color,
                            "gray"
                        ]
                    }]
            }

    return jsonify(fat_dict)


@app.route("/carbs-data.json")
def carbs_data():
    """Return percentage of carbs for the five saved recipes."""

    user = User.query.get(session["user_id"])
    # plan = Plan.query.filter_by(user_id=user.user_id).order_by(desc(Plan.plan_id)).first()
    plan = Plan.query.get(session["plan_id"])
    recipes = plan.recipes

    color = "#4A7E13"
    carbs = 0

    for recipe in recipes:
        carbs += recipe.carbohydrates

    carbs = (carbs*3)/5

    if carbs > 100:
        carbs = 100
        color = "#E04732"

    carbs_dict = {
                "labels": [
                    "Carbohydrates",
                    "Remainder",
                ],
                "datasets": [
                    {
                        "data": [carbs, 100-carbs],
                        "backgroundColor": [
                            color,
                            "gray"
                        ],
                        "hoverBackgroundColor": [
                            color,
                            "gray"
                        ]
                    }]
            }

    return jsonify(carbs_dict)


@app.route("/protein-data.json")
def protein_data():
    """Return percentage of protein for the five saved recipes."""

    user = User.query.get(session["user_id"])
    # plan = Plan.query.filter_by(user_id=user.user_id).order_by(desc(Plan.plan_id)).first()
    plan = Plan.query.get(session["plan_id"])
    recipes = plan.recipes

    color = "#4A7E13"
    protein = 0

    for recipe in recipes:
        protein += recipe.protein

    protein = (protein*3)/5

    if protein > 100:
        protein = 100
        color = "#E04732"

    protein_dict = {
                "labels": [
                    "Protein",
                    "Remainder",
                ],
                "datasets": [
                    {
                        "data": [protein, 100-protein],
                        "backgroundColor": [
                            color,
                            "gray"
                        ],
                        "hoverBackgroundColor": [
                            color,
                            "gray"
                        ]
                    }]
            }

    return jsonify(protein_dict)


######### Helper functions ##########

def make_recipe_search_request(number, cuisine, exclude, intolerant):
    search_url = "{}/recipes/search?".format(domain_url)
    offset = random.randint(0, 100)
    print "This is the offset: {}".format(offset)

    params = {
               "number": number,
               "offset": offset,
               "query": "main course",
               "limitLicense": False,
               "instructionsRequired": True,
               "type": "main course",
               "diet": "vegetarian",
               "intolerances": intolerant,
               "excludeIngredients": exclude,
               "cuisine": cuisine
              }

    return unirest.get(
                        search_url,
                        headers=headers,
                        params=params
                       )


def make_nutrition_info_request(ids):
    nutrition_url = "{}/recipes/informationBulk?".format(domain_url)

    params = {"includeNutrition": True,
                        "ids": ids
                        }

    return unirest.get(nutrition_url,
                            headers=headers,
                            params=params
                            )


if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    connect_to_db(app)
    app.run("0.0.0.0", debug=True)

