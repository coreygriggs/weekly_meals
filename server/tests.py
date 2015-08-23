import requests
import itertools
import random
import unittest


class MealsTest(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://localhost:5000"

    @property
    def rand_string(self):
        curr_string, alpha = '', 'abcdefghijklmnopqrstuvwxyz'
        for _ in itertools.repeat(None, 15):
            curr_string += random.choice(alpha)
        return curr_string

    def test_create_meal_posts_meal(self):
        data = {"meal_name": self.rand_string}
        post_request = requests.post(self.base_url + '/api/meals', data=data)
        self.assertIn(data['meal_name'], post_request.json().values())

    def test_get_meals_gets_all_meals_status_code(self):
        get_request = requests.get(self.base_url + '/api/meals')
        self.assertEqual(get_request.status_code, 200)

    def test_post_then_get_returns_meal(self):
        data = {"meal_name": self.rand_string}
        post_request = requests.post(self.base_url + '/api/meals', data=data)
        self.assertIn(data['meal_name'], post_request.json().values())

    def test_pass_ingredients_returns_new_ingredients(self):
        data = {"meal_name": self.rand_string, "ingredients": ['1']}
        post_request = requests.post(self.base_url + '/api/meals', data=data)
        for ingredient in data['ingredients']:
            response_ingredients = [ingredient.keys()[0] for ingredient in post_request.json()["ingredients"]]
            self.assertIn(ingredient.keys()[0], response_ingredients)

    def test_pass_new_ingredient_with_ingredient_name(self):
        data = {'ingredient_name': self.rand_string}
        post_request = requests.post(self.base_url + '/api/ingredients', data=data)
        self.assertEqual(post_request.status_code, 201)
        self.assertIn(data['ingredient_name'], post_request.json().values())

    def test_pass_new_ingredient_with_no_name(self):
        data = {'ingre': 'blorg'}
        post_request = requests.post(self.base_url + '/api/ingredients', data=data)
        self.assertEqual(post_request.status_code, 500)

    def test_update_ingredient_new_name(self):
        data = {'ingredient_name': self.rand_string}
        base_ingredient = requests.post(self.base_url + '/api/ingredients', data=data)
        updated_ingredient = {'ingredient_name': self.rand_string}
        updated = requests.patch(self.base_url + '/api/ingredients/%s' % base_ingredient.json().keys()[0], data=updated_ingredient)
        self.assertEqual(updated_ingredient['ingredient_name'], updated.json().values()[0])

    def tearDown(self):
        pass


if __name__ in ('main', '__main__'):
    unittest.main()