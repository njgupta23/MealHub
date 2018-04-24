import unittest

from server import app
from flask import session
from model import connect_to_db, db, example_data, User, Recipe, Plan, PlanRecipe
import datetime

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
        connect_to_db(app, "postgresql:///testdb")
        db.drop_all()
        self.client = app.test_client()
        app.config['TESTING'] = True
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


class AppTestsDatabase(unittest.TestCase):
    """Tests that use the database."""

    def setUp(self):
        connect_to_db(app, "postgresql:///testdb")
        db.drop_all()
        self.client = app.test_client()
        app.config['TESTING'] = True
        db.create_all()
        example_data()

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_create_account(self):
        """Test create account route."""

        with self.client as c:
            result = c.post("/new-account",
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
            self.assertIn("no meal plans yet", result.data)
            self.assertEqual(session["user_id"], 2)


class AppTestsSavedRecipe(unittest.TestCase):
    """Tests that use the saved recipes."""

    def setUp(self):
        connect_to_db(app, "postgresql:///testdb")
        db.drop_all()
        self.client = app.test_client()
        app.config['TESTING'] = True
        db.create_all()
        example_data()


    def test_saved_recipes(self):
        """Test saved-recipes route."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'
                sess['plan_id'] = '1'

        result = self.client.post("/save-recipes", data={"recipe-1": '{"protein":14.42,"carbs":8.78,"fat":40.32,"prepTime":20,"image":"https://spoonacular.com/recipeImages/479101-556x370.jpg","url":"http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/","title":"On the Job: Pan Roasted Cauliflower From Food52","id":479101}',
                                                         "recipe-2": '{"protein":14.42,"carbs":8.78,"fat":40.32,"prepTime":20,"image":"https://spoonacular.com/recipeImages/479101-556x370.jpg","url":"http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/","title":"On the Job: Pan Roasted Cauliflower From Food52","id":479101}',
                                                         "recipe-3": '{"protein":14.42,"carbs":8.78,"fat":40.32,"prepTime":20,"image":"https://spoonacular.com/recipeImages/479101-556x370.jpg","url":"http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/","title":"On the Job: Pan Roasted Cauliflower From Food52","id":479101}',
                                                         "recipe-4": '{"protein":14.42,"carbs":8.78,"fat":40.32,"prepTime":20,"image":"https://spoonacular.com/recipeImages/479101-556x370.jpg","url":"http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/","title":"On the Job: Pan Roasted Cauliflower From Food52","id":479101}',
                                                         "recipe-5": '{"protein":28.15,"carbs":23.16,"fat":11.87,"prepTime":20,"image":"https://spoonacular.com/recipeImages/604221-556x370.jpg","url":"http://damndelicious.net/2014/07/02/panda-express-chow-mein-copycat/","title":"Panda Express Chow Mein Copycat","id":604221}'},
                                                   follow_redirects=True)
        self.assertIn("On the Job: Pan Roasted Cauliflower From Food52", result.data)
        self.assertIn("Panda Express", result.data)

    def test_fat_data(self):
        """Test fat_data route to be used to create fat chart on my-meals page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'
                sess['plan_id'] = '1'

            result = c.get("/fat-data.json")
            self.assertIn("Fat", result.data)

    def test_carbs_data(self):
        """Test carbs_data route to be used to create carbs chart on my-meals page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'
                sess['plan_id'] = '1'

            result = c.get("/carbs-data.json")
            self.assertIn("Carbohydrates", result.data)

    def test_protein_data(self):
        """Test protein_data route to be used to create protein chart on my-meals page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'
                sess['plan_id'] = '1'

            result = c.get("/protein-data.json")
            self.assertIn("Protein", result.data)


class AppTestsSignedOut(unittest.TestCase):
    """Tests with user signed out of session."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_profile_page(self):
        """Test that user can't see profile page when signed out."""

        result = self.client.get("/profile", follow_redirects=True)
        self.assertNotIn("Choose a cuisine", result.data)


class AppTestsAPI(unittest.TestCase):
    """Tests that use the API."""

    def setUp(self):
        connect_to_db(app, "postgresql:///testdb")
        db.drop_all()
        self.client = app.test_client()
        app.config['TESTING'] = True
        db.create_all()
        example_data()
        class O(object):
            pass
        o = O()
        i = O()

        def _mock_recipe_search(number, cuisine, exclude, intolerant):
            o.body = {"results": [{
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            },{
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }, {
                "id": 479101,
                "title": "On the Job: Pan Roasted Cauliflower From Food52",
                "readyInMinutes": 20
            }
            ]}

            mock_search_results = o

            return mock_search_results

        def _mock_nutri_search(ids):
            i.body = [{"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }, {"id": 479101,
                      "sourceUrl": "http://feedmephoebe.com/2013/11/job-food52s-pan-roasted-cauliflower/",
                      "image": "https://spoonacular.com/recipeImages/479101-556x370.jpg",
                      "nutrition": {"nutrients": [{0: "blah"}, {"title": "Fat", "percentOfDailyNeeds": 40.32}, {0: "blah"}, {"title": "Carbohydrates", "percentOfDailyNeeds": 8.78}, {0: "blah"}, {0: "blah"}, {0: "blah"}, {"title": "Protein", "percentOfDailyNeeds": 14.42}]}
                    }
                    ]

            mock_nutri_results = i

            return mock_nutri_results

        import server
        server.make_recipe_search_request = _mock_recipe_search
        server.make_nutrition_info_request = _mock_nutri_search

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_process_search(self):
        """Test results route."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'

            result = c.post("/results", data=dict(
                start=datetime.date(2018, 4, 30),
                cuisine=["american"],
                exclude="",
                intolerant=""))

            self.assertIn("Pan Roasted Cauliflower From Food52", result.data)


if __name__ == "__main__":
    import unittest
    unittest.main()