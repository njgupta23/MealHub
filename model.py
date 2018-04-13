"""Models and database functions"""
from flask_sqlalchemy import SQLAlchemy

# connection to the PostgreSQL database
db = SQLAlchemy()

############################## Model definitions ###############################


class User(db.Model):
    """User of website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    pw = db.Column(db.String(20), nullable=False)
    bday = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String(1), nullable=False)

    saved_recipes = db.relationship("Recipe", secondary="assoc", backref="users")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} fname={} lname={}>".format(self.user_id, self.fname, self.lname)


class Recipe(db.Model):
    """Saved recipe on website (from Spoonacular API)."""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, primary_key=True)
    num_saved = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    image = db.Column(db.String(250), nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    fat = db.Column(db.Integer, nullable=False)
    carbohydrates = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Recipe recipe_id={} title={} num_saved={}>".format(self.recipe_id, self.title, self.num_saved)


class UserRecipe(db.Model):
    """User of website."""

    __tablename__ = "assoc"

    assoc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), index=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), index=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Assoc assoc_id={} user_id={} recipe_id={}>".format(self.assoc_id, self.user_id, self.recipe_id)


############################## Helper Functions ###############################

def connect_to_db(app):
    """Connect the database to the Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///testdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB"


