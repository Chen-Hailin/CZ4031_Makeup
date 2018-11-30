import os
from flask import Flask
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()


def create_app():
    print("creating app with name " + str(__name__))
    app = Flask(__name__, static_url_path='/static')
    app.config.update({'SECRET_KEY': 'FORM_CSRF'})
    bootstrap.init_app(app)
    return app
