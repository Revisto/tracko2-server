
import requests
from flask import Blueprint, request
from models import Authentication

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods = ['POST'])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    signup_answer = Authentication().signup(username, password)
    return signup_answer

@auth.route("/login", methods = ['POST'])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    signup_answer = Authentication().signup(username, password)
    return signup_answer

@auth.route("/is_username_unique", methods = ['POST'])
def is_username_unique():
    username = request.form.get('username')
    is_it_unique_json = Authentication().is_username_unique(username)
    return is_it_unique_json