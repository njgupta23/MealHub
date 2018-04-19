import unittest

from server import app
from flask import session
from model import connect_to_db, db, example_data, User, Recipe, UserRecipe

class AppTestsBasic(unittest.TestCase):
    """Basic tests for this web app."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, "postgresql:///testdb")

    def test_homepage(self):
        """Test homepage route."""

        result = self.client.get("/")
        self.assertIn("Don't know what to eat?", result.data)

    def test_signin_page(self):
        """Test sign in form."""

        result = self.client.get("/signin")
        self.assertIn("Sign In", result.data)


class AppTestsSignInSignOut(unittest.TestCase):
    """Test sign in and sign out."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()

    def test_signin(self):
        """Test sign in route."""

        with self.client as c:
            result = c.post("/signin",
                                      data={
                                            "fname": "Bilbo",
                                            "lname": "Baggins",
                                            "email": "bilbo@gmail.com",
                                            "bday": "2000-01-01 00:00:00",
                                            "gender": "m",
                                            "pw": "bilbo"
                                            },
                                      follow_redirects=True
                                      )
            self.assertIn("Hello, Bilbo", result.data)
            self.assertIn("Choose a cuisine", result.data)
            self.assertEqual(session["user_id"], 1)

            result2 = c.post("/signin",
                                      data={
                                            "fname": "Harry",
                                            "lname": "Potter",
                                            "email": "harry@gmail.com",
                                            "bday": "2000-01-01 00:00:00",
                                            "gender": "m",
                                            "pw": "harry"
                                            },
                                      follow_redirects=True
                                      )
            self.assertIn("No such user", result2.data)

            result3 = c.post("/signin",
                                      data={
                                            "fname": "Bilbo",
                                            "lname": "Baggins",
                                            "email": "bilbo@gmail.com",
                                            "bday": "2000-01-01 00:00:00",
                                            "gender": "m",
                                            "pw": "harry"
                                            },
                                      follow_redirects=True
                                      )
            self.assertIn("Incorrect password", result3.data)

    def test_signout(self):
        """Test sign out route."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'

            result = self.client.get("/signout", follow_redirects=True)
            self.assertIn("Don't know what to eat?", result.data)
            self.assertNotIn('user_id', session)


class AppTestsCreateAccount(unittest.TestCase):
    """Tests with user signed in to session."""

    def setUp(self):
        db.drop_all()
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_create_account(self):
        """Test create account route."""

        with self.client as c:
            result = c.post("/profile",
                                      data={
                                            "fname": "Frodo",
                                            "lname": "Baggins",
                                            "email": "frodo@gmail.com",
                                            "bday": "2000-05-05 00:00:00",
                                            "gender": "m",
                                            "pw": "frodo"
                                            },
                                      follow_redirects=True
                                      )
            self.assertIn("Hello, Frodo", result.data)
            self.assertIn("Choose a cuisine", result.data)
            self.assertEqual(session["user_id"], 2)


class AppTestsSignedOut(unittest.TestCase):
    """Tests with user signed out of session."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_profile_page(self):
        """Test that user can't see profile page when signed out."""

        result = self.client.get("/profile", follow_redirects=True)
        self.assertNotIn("Choose a cuisine", result.data)


class AppTestsResults(unittest.TestCase):
    """Tests the results route."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()

        def _mock_process_search(params):
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

            return mock_results

        app.make_recipe_search_request = _mock_process_search
        app.make_nutrition_info_request = _mock_process_search

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_process_search(self):
        """Test API requests and results route."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'

        result = self.client.get("/results", data={"cuisine": "american"})
        self.assertIn("Pan Roasted Cauliflower From Food52", result.data)



if __name__ == "__main__":
    import unittest
    unittest.main()
