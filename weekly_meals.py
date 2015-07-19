from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
import yaml
from datetime import datetime
import json
from util import converted_time

app = Flask(__name__)
db = SQLAlchemy(app)
config_file = open('config.yaml', 'r')
config = yaml.load(config_file)
app.config["SQLALCHEMY_DATABASE_URI"] = config["SQLALCHEMY_DATABASE_URI"]
app.config["DEBUG"] = config["DEBUG"]
meal_ingredient = db.Table('meal_ingredient',
                            db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), nullable=False),
                            db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), nullable=False),
                            db.PrimaryKeyConstraint('meal_id', 'ingredient_id'))


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime, default=datetime.now())
    ingredient_name = db.Column(db.String(256), unique=True)


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime, default=datetime.now())
    meal_name = db.Column(db.String(256))
    ingredients = db.relationship('Ingredient', secondary=meal_ingredient)


class MealAPI():

    def get(self, meal_id):
        meal = db.session.query(Meal).filter(Meal.id == meal_id).first()
        if meal is None:
            return jsonify({"error": "This meal does not exist"})
        return json.dumps({"id": meal.id, "created": converted_time(meal.created), "updated": converted_time(meal.updated),
                           "meal_name": meal.meal_name, "ingredients": meal.ingredients})

    def post(self, meal):
        meal = json.loads(meal)
        db.session.add(Meal(meal))
        db.session.commit()

    def put(self, meal_id, meal):
        db.session.execute(update(Meal).where(Meal.id == meal_id).values(json.loads(meal)))
        db.session.commit()
        updated_row = db.session.query(Meal).filter(Meal.id == meal_id).first()
        return json.dumps({"id": updated_row.id, "created": converted_time(updated_row.created),
                           "updated": converted_time(updated_row.updated),
                           "meal_name": updated_row.meal_name, "ingredients": updated_row.ingredients})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/meals/<int:meal_id>', methods=['GET', 'PUT'])
def meals(meal_id):
    meal_api = MealAPI()
    if request.method == 'GET':
        return meal_api.get(meal_id)
    elif request.method == 'PUT':
        print request.data
        return meal_api.put(meal_id, request.data)

if __name__ in ('main', '__main__'):
    app.run()