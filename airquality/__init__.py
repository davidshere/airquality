import logging
import os

from flask import Flask


logger = logging.getLogger(__name__)


def create_app(flask=Flask, test_config=None):
    # create and configure the app
    app = flask(
        __name__,
        instance_relative_config=True,
        template_folder='build/',
        static_folder='build/static/'
    )
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'airquality.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import readings
    app.register_blueprint(readings.bp)

    return app

