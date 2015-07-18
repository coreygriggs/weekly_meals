from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import yaml

app = Flask(__name__)
db = SQLAlchemy(app)
config_file = open('config.yaml', 'r')
config = yaml.load(config_file)
meal_ingredients = db.Table('meal_ingredients',
                            db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), nullable=False),
                            db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), nullable=False),
                            db.PrimaryKeyConstraint('meal_id', 'ingredient_id'))


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    ingredient_name = db.Column(db.String(256), unique=True)


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_name = db.Column(db.String(256))
    ingredients = db.relationship('Ingredients', secondary=meal_ingredients)


@app.route('/')
def index():
    return "hi"


if __name__ in ('main', '__main__'):
    app.run()