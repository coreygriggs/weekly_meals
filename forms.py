__author__ = 'coreygriggs'

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class MealForm(Form):
    meal_name = StringField('Meal Name', validators=[DataRequired()])