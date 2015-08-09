from flask import (Flask, render_template, jsonify, request, flash, redirect, url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
import yaml
from datetime import datetime
import json
from util import converted_time
from forms import MealForm


app = Flask(__name__)
db = SQLAlchemy()
db.init_app(app)
config_file = open('config.yaml', 'r')
config = yaml.load(config_file)
app.config["SQLALCHEMY_DATABASE_URI"] = config["SQLALCHEMY_DATABASE_URI"]
app.config["DEBUG"] = config["DEBUG"]
app.config["SECRET_KEY"] = config["SECRET_KEY"]
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


class MealAPI():

    def format_meal_res(self, meal):
        """
	    Wrapper around a meal result row
	    :param meal: A sqlalchemy row object
	    :return: A json string
        """
        return json.dumps({"id": meal.id, "created": converted_time(meal.created), "updated": converted_time(meal.updated),
                           "meal_name": meal.meal_name, "ingredients": meal.ingredients})

    def get(self, meal_id=None):
        if meal_id is None:
            return db.session.query(Meal).order_by(Meal.id.desc()).limit(10)
        meal = db.session.query(Meal).filter(Meal.id == meal_id).first()
        if meal is None:
            return jsonify({"error": "This meal does not exist"})
        return meal

    def post(self, meal):
        meal = json.loads(meal)
        meal["created"] = datetime.utcnow()
        db.session.add(Meal(**meal))
        db.session.commit()
        return json.dumps({"success": "Meal %s has been created" % meal["meal_name"]})

    def put(self, meal_id, meal):
        db.session.execute(update(Meal).where(Meal.id == meal_id).values(meal_name=meal))
        db.session.commit()
        updated_row = db.session.query(Meal).filter(Meal.id == meal_id).first()
        return updated_row

    def delete(self, meal_id):
        meal = db.session.query(Meal).filter(Meal.id==meal_id).first()
        db.session.delete(meal)
        db.session.commit()
        return {"success": "%s has been deleted" % meal.meal_name}


@app.route('/', methods=['GET', 'POST'])
def index():
    form = MealForm()
    last_ten_meals = MealAPI().get()
    if request.method == 'GET':
        return render_template('index.html', form=form, meals=last_ten_meals)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if request.method == 'POST':
                new_meal = Meal(meal_name=form.meal_name.data, created=datetime.utcnow())
                db.session.add(new_meal)
                db.session.commit()
                return render_template('index.html', form=form, meals=last_ten_meals)


@app.route('/meals/<int:meal_id>', methods=['GET', 'POST', 'DELETE'])
def meals(meal_id):
    meal_api = MealAPI()
    form = MealForm()
    if request.method == 'GET':
        this_meal = meal_api.get(meal_id)
        return render_template('meal.html', meal=this_meal, form=form)
    elif request.method == 'POST':
        meal_update = meal_api.put(meal_id, form.meal_name.data)
        return render_template('meal.html', meal=meal_update, form=form)
    elif request.method == 'DELETE':
        deleted_meal = meal_api.delete(meal_id)
        flash("%s" % deleted_meal['success'])
        return redirect(url_for('index'))



if __name__ in ('main', '__main__'):
    app.run()