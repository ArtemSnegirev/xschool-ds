"""Initiates the API through Flask's blueprint"""

from flask import Blueprint

api = Blueprint('api', __name__)

# you should import new routes here

from ...app.api import support_department
