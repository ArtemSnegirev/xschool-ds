"""This is the views page, which is similar to what the routes do for the API.
The difference is rather than routes, this renders and displays HTML pages"""

from . import main
from flask import render_template


@main.route('/')
def index():
    return render_template('index.html')
