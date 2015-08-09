import unittest
import weekly_meals


class MealsTest(unittest.TestCase):

    def setUp(self):
        weekly_meals.app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
        weekly_meals.app.config['TESTING'] = True
        self.app = weekly_meals.app.test_client()
        with weekly_meals.app.app_context():
            weekly_meals.init_db()

    def test_create_meal_posts_meal(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        with weekly_meals.app.app_context():
            weekly_meals.db.drop_all()


if __name__ in ('main', '__main__'):
    unittest.main()