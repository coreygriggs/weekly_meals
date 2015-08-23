__author__ = 'coreygriggs'

from flask.ext.api import FlaskAPI, exceptions, status
from flask import request, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
import yaml
from datetime import datetime

app = FlaskAPI(__name__)
db = SQLAlchemy()
db.init_app(app)
config_file = open('config.yaml', 'r')
config = yaml.load(config_file)
app.config["SQLALCHEMY_DATABASE_URI"] = config["SQLALCHEMY_DATABASE_URI"]
app.config["DEBUG"] = config["DEBUG"]
app.config["SECRET_KEY"] = config["SECRET_KEY"]
app.config["DEFAULT_RENDERERS"] = config["DEFAULT_RENDERERS"]

meal_ingredient = db.Table('meal_ingredient',
                            db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), nullable=False),
                            db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), nullable=False),
                            db.PrimaryKeyConstraint('meal_id', 'ingredient_id'))


def init_db():
    db.init_app(app)
    db.create_all()


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime, default=datetime.utcnow())
    ingredient_name = db.Column(db.String(256), unique=True)


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime, default=datetime.utcnow())
    meal_name = db.Column(db.String(256))
    ingredients = db.relationship('Ingredient', secondary=meal_ingredient)


@app.route('/api/meals', methods=['GET', 'POST'])
def meals():
    if request.method == 'POST':
        new_meal = request.data
        if 'meal_name' not in new_meal.keys():
            return exceptions.NotAcceptable()
        db_meal = Meal(meal_name=new_meal["meal_name"])
        db.session.add(db_meal)
        if 'ingredients' in new_meal:
            for ingredient_item in new_meal['ingredients']:
                meal_ingredient.insert().values(meal_id=db_meal, ingredient_id=ingredient_item)
            ingredient_data = [{ingredient.id: ingredient.ingredient_name} for ingredient in db.session.query(Ingredient).\
	        filter(Ingredient.id.in_(new_meal['ingredients'])).all()]
            db.session.commit()
            return {db_meal.id: db_meal.meal_name, "ingredients": ingredient_data}, status.HTTP_201_CREATED
        else:
            db.session.commit()
            return {db_meal.id: db_meal.meal_name}, status.HTTP_201_CREATED
    else:
        meals = db.session.query(Meal).all()
        if len(meals) >= 1:
            return [{meal.id: meal.meal_name, "ingredients": [ing_id for ing_id in db.session.query(meal_ingredient).\
	                                                          filter(meal_ingredient.c.meal_id==meal.id)]} for meal in meals]
        else:
            return {"success": "no meals have been created"}

@app.route('/api/meals/<int:meal_id>')
def meal(meal_id):
    meal = db.session.query(Meal).filter(Meal.id==meal_id).first()
    if meal is not None:
        return {meal.id: meal.meal_name}
    else:
        return exceptions.NotFound()

@app.route('/api/ingredients', methods=['GET', 'POST'])
def ingredients():
    if request.method == 'POST':
        if 'ingredient_name' not in request.data.keys():
            return exceptions.NotAcceptable()
        new_ingredient = Ingredient(ingredient_name=request.data['ingredient_name'])
        db.session.add(new_ingredient)
        db.session.commit()
        return {new_ingredient.id: new_ingredient.ingredient_name}, status.HTTP_201_CREATED
    ingredients = db.session.query(Ingredient).all()
    return [{ingredient.id: ingredient.ingredient_name} for ingredient in ingredients]

@app.route('/api/ingredients/<int:ingredient_id>', methods=['GET', 'PATCH'])
def ingredient(ingredient_id):
    if request.method == 'PATCH':
        db.session.execute(update(Ingredient).where(Ingredient.id==ingredient_id).values(ingredient_name=request.data['ingredient_name']))
        db.session.commit()
        new_ingredient = db.session.query(Ingredient).filter(Ingredient.id==ingredient_id).first()
        return {new_ingredient.id: new_ingredient.ingredient_name}
    ingredient = db.session.query(Ingredient).filter(Ingredient.id==ingredient_id).first()
    if ingredient is not None:
        return {ingredient.id: ingredient.ingredient_name}
    else:
        raise exceptions.NotFound()

if __name__ in ('main', '__main__'):
    app.run()
