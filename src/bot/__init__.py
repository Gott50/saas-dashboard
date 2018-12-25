from .bot import Bot
from .answers import Answers

import os

from flask import Flask


def create_app(script_info=None):
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # shell context for flask cli
    app.shell_context_processor({'app': app})

    return app
