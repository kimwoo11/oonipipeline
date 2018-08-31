# === Uncomment to run project locally: === #
# import sys
# import os
#
# src_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(src_root_dir)

from flask import Flask
from oonipipeline.models.models import db
from oonipipeline.controllers import web_pages
from oonipipeline.controllers import api


BLUEPRINTS = [
    (web_pages.web_pages_bp, '/'),
    (api.api_bp, '/api')
]


def register_blueprints(app, blueprints):
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    register_blueprints(app, BLUEPRINTS)
    db.init_app(app)
    return app


""" Build app (init databases) """
app = create_app("oonipipeline.config")
db.drop_all(app=create_app("oonipipeline.config"))
db.create_all(app=create_app("oonipipeline.config"))
app.run(debug=False, port=8000)

