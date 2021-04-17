
import requests
from flask import Blueprint, request, abort
from models import Authentication, Database, User

user = Blueprint("user", __name__)

def is_api_key_valid(func):
    def is_api_key_valid_(*args, **kwargs):
        api_key = request.form.get("api_key")
        if Authentication().is_api_key_valid(api_key) is False:
            abort(401)
        return func(*args, **kwargs)
    return is_api_key_valid_

@is_api_key_valid
@user.route("/shelves", methods = ['POST'])
def shelves():
    api_key = request.form.get("api_key")
    return Database().get_all_shelves(api_key)

@is_api_key_valid
@user.route("/shelf/<shelf_name>", methods = ['POST'])
def specific_shelf(shelf_name):
    api_key = request.form.get("api_key")
    return User().get_specific_shelf(api_key, shelf_name)

@is_api_key_valid
@user.route("/add/series", methods = ['POST'])
def add_series():
    api_key = request.form.get("api_key")
    series_name = request.form.get("series_name")
    shelf_name = request.form.get("shelf_name")
    return User().add_series_to_shelf(api_key, shelf_name, series_name)


@is_api_key_valid
@user.route("/move/series", methods = ['POST'])
def move_series():
    api_key = request.form.get("api_key")
    series_name = request.form.get("series_name")
    from_shelf = request.form.get("from_shelf")
    to_shelf = request.form.get("to_shelf")
    return User().move_series_to_shelf(api_key, series_name, from_shelf, to_shelf)

@is_api_key_valid
@user.route("/update/series", methods = ['POST'])
def update_series():
    api_key = request.form.get("api_key")
    series_name = request.form.get("series_name")
    shelf = request.form.get("shelf")
    watched_till = request.form.get("watched_till")
    return User().update_series(api_key, series_name, shelf, watched_till)