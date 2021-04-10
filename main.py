from flask import Flask, request, redirect
from models import Authentication

# importing views
from views.api.auth import auth

app = Flask(__name__)


def fix_extra_slash_at_the_end_of_the_url():
    if request.full_path.count("/") > 1 and request.full_path.endswith("/?"):
        return redirect(request.full_path[0:-2])


app.before_request(fix_extra_slash_at_the_end_of_the_url)
# registering blueprints

app.register_blueprint(auth, url_prefix='/api/')
