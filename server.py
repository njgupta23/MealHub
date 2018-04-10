import os
import unirest
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Recipe, UserRecipe


app = Flask(__name__)
app.secret_key = "secret..."

#SPOONACULAR_KEY = os.environ['SPOONACULAR_KEY']


# response = unirest.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/searchComplex?",
#   headers={
#     "X-Mashape-Key": "nAiQmpcpwZmsh6s601aNDvJCwVZjp1EzxBdjsnZZ0a0c585kU0",
#     "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com",
#     "Accept": "application/json",
#   },
#   params={
#     "minProtein": 5,
#     "maxFat": 100,
#     "number": 10,
#     "maxCalories": 1500,
#     "minCarbs": 5,
#     "ranking": 2,
#     "query": "burger",
#     "excludeIngredients": "coconut,mango",
#     "offset": 0,
#     "maxCarbs": 100,
#     "diet": "vegetarian"
#     "intolerances": "peanut,shellfish",
#     "cuisine": "american",
#     "minFat": 5,
#     "type": "main course",
#     "maxProtein": 100,
#     "includeIngredients": "onions,lettuce,tomato",
#     "minCalories": 150,
#     "limitLicense": False
#   }
# )


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


######### Helper functions ##########

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    connect_to_db(app)
    app.run("0.0.0.0", debug=True)

