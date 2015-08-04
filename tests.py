__author__ = 'coreygriggs'

import unittest
from flask import Flask
import yaml
from sqlalchemy import create_engine
from multiprocessing import Process
import requests


class TestMealsApi(unittest.TestCase):

    def create_app(self, db_uri, debug=False):
        app = Flask(__name__)
        app.debug = debug
        app.engine = create_engine(db_uri)
        return app

    def setUp(self):
        self.config_file = open('test_config.yaml', 'r')
        self.config = yaml.load(self.config_file)
        self.app = self.create_app(self.config["SQLALCHEMY_DATABASE_URI"], debug=True)
        self.requests = requests

    # def test_post_valid_meal_request(self):
    #     self.requests.post('http://localhost:5000/meals/%s' % )


if __name__ in ('main', '__main__'):
    unittest.main()